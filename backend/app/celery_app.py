from celery import Celery
from sqlalchemy.orm import Session

from .database import SessionLocal
from . import crud
from .notifications import send_fcm_notification

# Celery instance
celery_app = Celery(
    "geofence",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)


@celery_app.task
def process_alert_task(user_id: int, geofence_id: int | None, message: str) -> None:
    """
    Background task to create an alert record and send push notifications.
    """
    db: Session = SessionLocal()
    try:
        # 1. Create alert record
        alert = crud.create_alert(db, user_id=user_id, geofence_id=geofence_id, message=message)

        # 2. Fetch user's devices
        devices = crud.get_devices_for_user(db, user_id=user_id)

        # 3. Send push notification to each device
        title = "Geofence Alert"
        body = message

        for device in devices:
            print(f"Sending FCM to user {user_id} device {device.id}...")
            send_fcm_notification(
                token=device.fcm_token,
                title=title,
                body=body,
                data={
                    "alert_id": alert.id,
                    "user_id": user_id,
                    "geofence_id": geofence_id or 0,
                },
            )

    finally:
        db.close()
