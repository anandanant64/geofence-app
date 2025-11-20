import math
from typing import List

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from .database import Base, engine, SessionLocal
from . import models, schemas, crud
from .celery_app import process_alert_task

# Create DB tables (dev mode)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Geofence MVP")


# ---------- DB SESSION DEPENDENCY ----------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- HELPER: HAVERSINE DISTANCE ----------

def haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Returns distance in meters between two lat/lon points using the Haversine formula.
    """
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


# ---------- ROUTES ----------

@app.get("/")
def read_root():
    return {"message": "Geofence MVP API is running"}


# ---- Users ----

@app.post("/users/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create a simple user (just username for now).
    Required before creating geofences, because geofences.user_id has a FK to users.id.
    """
    return crud.create_user(db, user)


# ---- Geofences ----

@app.post("/geofences/", response_model=schemas.GeofenceResponse)
def create_geofence(geofence: schemas.GeofenceCreate, db: Session = Depends(get_db)):
    """
    Create a circular geofence for a given user.
    Validates that the user exists to avoid foreign key errors.
    """
    db_user = crud.get_user(db, geofence.user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    return crud.create_geofence(db, geofence)


# ---- Device registration ----

@app.post("/devices/register", response_model=schemas.DeviceResponse)
def register_device(device: schemas.DeviceRegister, db: Session = Depends(get_db)):
    """
    Register or update a device's FCM token for a user.
    The mobile app should call this after it gets an FCM token from Firebase.
    """
    db_user = crud.get_user(db, device.user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    return crud.register_device(db, device)


# ---- Location Updates & Geofence Check ----

@app.post("/location/update", response_model=schemas.LocationCheckResult)
def update_location(location: schemas.LocationUpdate, db: Session = Depends(get_db)):
    """
    Save or update the user's latest location and check against their geofence.
    For now:
      - Uses the first geofence for the user (if multiple exist).
      - Returns inside/outside, distance, and a basic alert flag (alert if outside).
      - If alert is true, we enqueue a background task to log an Alert + send push.
    """
    # Ensure user exists
    db_user = crud.get_user(db, location.user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Persist latest location
    crud.upsert_user_location(db, location)

    # Get user's geofences
    geofences = crud.get_user_geofences(db, location.user_id)
    if not geofences:
        raise HTTPException(status_code=400, detail="User has no geofences configured")

    # For now, just use the first geofence
    gf = geofences[0]

    distance = haversine_distance_m(
        location.lat,
        location.lon,
        gf.center_lat,
        gf.center_lon,
    )

    inside = distance <= gf.radius_m
    alert = not inside  # basic rule: alert when outside

    # If outside, enqueue background task to log alert and send push
    if alert:
        message = "User is outside geofenced area"
        process_alert_task.delay(location.user_id, gf.id, message)

    return schemas.LocationCheckResult(
        inside=inside,
        distance_m=distance,
        alert=alert,
    )


# ---- Alerts ----

@app.get("/alerts/", response_model=List[schemas.AlertResponse])
def list_alerts(limit: int = 100, db: Session = Depends(get_db)):
    """
    List recent alerts (for debugging / admin).
    """
    return crud.get_alerts(db, limit=limit)


@app.get("/users/{user_id}/alerts", response_model=List[schemas.AlertResponse])
def list_user_alerts(user_id: int, limit: int = 100, db: Session = Depends(get_db)):
    """
    List recent alerts for a specific user.
    """
    db_user = crud.get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    return crud.get_alerts_for_user(db, user_id=user_id, limit=limit)

@app.get("/users/{user_id}/profile", response_model=schemas.UserProfileResponse)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """
    Return full user information:
      - basic user details
      - all geofences
      - all registered devices
      - last known location (if any)
      - recent alerts
    """
    db_user = crud.get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    geofences = crud.get_user_geofences(db, user_id=user_id)
    devices = crud.get_devices_for_user(db, user_id=user_id)
    last_location = crud.get_last_location_for_user(db, user_id=user_id)
    alerts = crud.get_alerts_for_user(db, user_id=user_id, limit=50)

    return schemas.UserProfileResponse(
        user=db_user,
        geofences=geofences,
        devices=devices,
        last_location=last_location,
        alerts=alerts,
    )

