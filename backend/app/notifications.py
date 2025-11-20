import os
import json
from typing import Dict, Any

import requests
from dotenv import load_dotenv
from google.oauth2 import service_account
from google.auth.transport.requests import Request as GoogleRequest

# Load environment variables
load_dotenv()

SERVICE_ACCOUNT_FILE = os.getenv("FCM_SERVICE_ACCOUNT_FILE")

if not SERVICE_ACCOUNT_FILE:
    print("WARNING: FCM_SERVICE_ACCOUNT_FILE is not set. Push notifications will not work.")


def _get_fcm_access_token() -> str | None:
    """
    Uses the service account JSON to obtain an OAuth2 access token
    with the firebase.messaging scope.
    """
    if not SERVICE_ACCOUNT_FILE or not os.path.exists(SERVICE_ACCOUNT_FILE):
        print("Service account file not found. Cannot obtain FCM access token.")
        return None

    scopes = ["https://www.googleapis.com/auth/firebase.messaging"]

    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=scopes,
        )
        # Refresh to get token
        auth_req = GoogleRequest()
        credentials.refresh(auth_req)
        return credentials.token
    except Exception as e:
        print(f"Error getting FCM access token: {e}")
        return None


def _get_project_id_from_service_account() -> str | None:
    """
    Reads the project_id from the service account JSON file.
    """
    if not SERVICE_ACCOUNT_FILE or not os.path.exists(SERVICE_ACCOUNT_FILE):
        print("Service account file not found. Cannot read project_id.")
        return None

    try:
        with open(SERVICE_ACCOUNT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("project_id")
    except Exception as e:
        print(f"Error reading project_id from service account: {e}")
        return None


def send_fcm_notification(token: str, title: str, body: str, data: Dict[str, Any] | None = None) -> bool:
    """
    Sends a push notification to a single device using FCM HTTP v1 API.
    Returns True on success, False otherwise.
    """

    project_id = _get_project_id_from_service_account()
    if not project_id:
        print("No project_id available. Cannot send FCM notification.")
        return False

    access_token = _get_fcm_access_token()
    if not access_token:
        print("No access token available. Cannot send FCM notification.")
        return False

    # 🔴 FCM requires ALL data values to be strings
    data_str: Dict[str, str] = {}
    if data:
        data_str = {str(k): str(v) for k, v in data.items()}

    url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    payload: Dict[str, Any] = {
        "message": {
            "token": token,
            "notification": {
                "title": title,
                "body": body,
            },
            "data": data_str,
        }
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
        if response.status_code == 200:
            return True
        else:
            print(f"FCM v1 error {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"Error sending FCM v1 notification: {e}")
        return False

