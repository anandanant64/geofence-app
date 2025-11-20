from datetime import datetime
from pydantic import BaseModel


# ---------- USER SCHEMAS ----------

class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True


# ---------- LOCATION & GEOFENCE SCHEMAS ----------

class LocationUpdate(BaseModel):
    user_id: int
    lat: float
    lon: float


class GeofenceCreate(BaseModel):
    user_id: int
    center_lat: float
    center_lon: float
    radius_m: float


class GeofenceResponse(BaseModel):
    id: int
    user_id: int
    center_lat: float
    center_lon: float
    radius_m: float

    class Config:
        from_attributes = True


class LocationCheckResult(BaseModel):
    inside: bool
    distance_m: float
    alert: bool


# ---------- ALERT SCHEMA ----------

class AlertResponse(BaseModel):
    id: int
    user_id: int
    geofence_id: int | None = None
    message: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- DEVICE SCHEMAS ----------

class DeviceRegister(BaseModel):
    user_id: int
    platform: str
    fcm_token: str


class DeviceResponse(BaseModel):
    id: int
    user_id: int
    platform: str
    fcm_token: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserLocationResponse(BaseModel):
    id: int
    user_id: int
    lat: float
    lon: float
    updated_at: datetime

    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    user: UserResponse
    geofences: list[GeofenceResponse]
    devices: list[DeviceResponse]
    last_location: UserLocationResponse | None
    alerts: list[AlertResponse]