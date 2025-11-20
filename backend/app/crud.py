from sqlalchemy.orm import Session

from . import models, schemas


# ---------- USER CRUD ----------

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(username=user.username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int) -> models.User | None:
    return db.query(models.User).filter(models.User.id == user_id).first()


# ---------- GEOFENCE CRUD ----------

def create_geofence(db: Session, geofence: schemas.GeofenceCreate) -> models.Geofence:
    db_geofence = models.Geofence(
        user_id=geofence.user_id,
        center_lat=geofence.center_lat,
        center_lon=geofence.center_lon,
        radius_m=geofence.radius_m,
    )
    db.add(db_geofence)
    db.commit()
    db.refresh(db_geofence)
    return db_geofence


def get_user_geofences(db: Session, user_id: int) -> list[models.Geofence]:
    return db.query(models.Geofence).filter(models.Geofence.user_id == user_id).all()


# ---------- LOCATION CRUD ----------

def upsert_user_location(db: Session, location: schemas.LocationUpdate) -> models.UserLocation:
    existing = (
        db.query(models.UserLocation)
        .filter(models.UserLocation.user_id == location.user_id)
        .order_by(models.UserLocation.id.desc())
        .first()
    )

    if existing:
        existing.lat = location.lat
        existing.lon = location.lon
    else:
        existing = models.UserLocation(
            user_id=location.user_id,
            lat=location.lat,
            lon=location.lon,
        )
        db.add(existing)

    db.commit()
    db.refresh(existing)
    return existing


# ---------- ALERT CRUD ----------

def create_alert(db: Session, user_id: int, geofence_id: int | None, message: str) -> models.Alert:
    alert = models.Alert(
        user_id=user_id,
        geofence_id=geofence_id,
        message=message,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def get_alerts(db: Session, limit: int = 100) -> list[models.Alert]:
    return (
        db.query(models.Alert)
        .order_by(models.Alert.created_at.desc())
        .limit(limit)
        .all()
    )


def get_alerts_for_user(db: Session, user_id: int, limit: int = 100) -> list[models.Alert]:
    return (
        db.query(models.Alert)
        .filter(models.Alert.user_id == user_id)
        .order_by(models.Alert.created_at.desc())
        .limit(limit)
        .all()
    )


# ---------- DEVICE CRUD ----------

def register_device(db: Session, device: schemas.DeviceRegister) -> models.Device:
    """
    Simple upsert-like behavior:
    - If a device with same fcm_token exists, update its user/platform.
    - Else create a new row.
    """
    existing = db.query(models.Device).filter(models.Device.fcm_token == device.fcm_token).first()

    if existing:
        existing.user_id = device.user_id
        existing.platform = device.platform
        db.commit()
        db.refresh(existing)
        return existing

    new_device = models.Device(
        user_id=device.user_id,
        platform=device.platform,
        fcm_token=device.fcm_token,
    )
    db.add(new_device)
    db.commit()
    db.refresh(new_device)
    return new_device


def get_devices_for_user(db: Session, user_id: int) -> list[models.Device]:
    return db.query(models.Device).filter(models.Device.user_id == user_id).all()

def get_last_location_for_user(db: Session, user_id: int) -> models.UserLocation | None:
    return (
        db.query(models.UserLocation)
        .filter(models.UserLocation.user_id == user_id)
        .order_by(models.UserLocation.updated_at.desc())
        .first()
    )