📘 Geofence Monitoring System — Documentation

A full-stack geofencing and alerting platform that tracks user location, evaluates geofences, and triggers push notifications when a user exits a designated safe zone.

This system uses:

FastAPI backend

MySQL database

Celery with Redis for background processing

Firebase Cloud Messaging (FCM) for mobile push alerts

Flutter mobile client

Docker for database & Redis services

📚 Table of Contents

Overview

Architecture Summary

System Flow Diagram

Features

Technology Stack

Folder Structure

Installation (pre req install vs code and wsl 2 if working on windows)

Configuration

Running the System

API Endpoints

Testing Workflow

Troubleshooting

Future Enhancements

🚀 Overview

This project is a real-time geofence monitoring & alert system.
A mobile app periodically sends GPS coordinates to the backend.
The backend checks whether the user is inside or outside their assigned geofence.

If outside:

FastAPI creates an alert event

Celery processes it asynchronously

Celery sends a push notification via Firebase Cloud Messaging

Mobile app receives the alert instantly

This architecture supports thousands of users concurrently.

🏛️ Architecture Summary
Mobile App (Flutter)
     |
     |   POST /location/update
     v
FastAPI Backend ───> MySQL (users, geofences, locations, alerts)
     |
     |   Enqueue Task
     v
Redis (Broker) ───> Celery Worker
                          |
                          | Send FCM HTTP v1
                          v
                 Firebase Cloud Messaging
                          |
                          v
                  Mobile Push Notification

🎬 System Flow Diagram

A full animation of this flow is included here:

📹 Geofence Diagram Animation (MP4)
👉 Download: Add your link after uploading to repo or cloud

Static simplified diagram:

+--------------+      +---------------+      +-------------+
| Mobile App   | ---> |   FastAPI     | ---> |   MySQL     |
+--------------+      +---------------+      +-------------+
        |                      |
        |                      v
        |               +-------------+
        |               |   Redis     |
        |               +-------------+
        |                      |
        |                      v
        |                +-----------+
        |                |  Celery   |
        |                +-----------+
        |                      |
        |       FCM HTTP v1    v
        |                +------------+
        +--------------> | Firebase   |
                         +------------+

⭐ Features
✔ Core

Circular geofence support

Location updates via mobile client

Geofence exit detection

Alert creation & storage

Device registration (FCM token)

✔ Push alerts

FCM HTTP v1 integration

Token-based push notifications

Background task processing

✔ Monitoring

User profile endpoint (geofences, devices, last location, alerts)

Alerts listing API

System-ready logs using SQLAlchemy engine output

🧰 Technology Stack
Backend

FastAPI

SQLAlchemy ORM

MySQL

Celery

Redis

Pydantic

Uvicorn

Docker Compose

Mobile

Flutter

Firebase Core

Firebase Messaging

Push

Firebase Cloud Messaging (FCM HTTP v1)

Google Service Account Authentication

📁 Folder Structure
geofence-app/
│
├── backend/
│   ├── app/
│   │   ├── main.py                # FastAPI entrypoint
│   │   ├── crud.py                # DB operations
│   │   ├── models.py              # SQLAlchemy ORM models
│   │   ├── schemas.py             # Pydantic schemas
│   │   ├── celery_app.py          # Celery worker & tasks
│   │   ├── notifications.py       # FCM logic
│   │
│   ├── venv/                      # Python virtual environment
│   ├── requirements.txt           # For installation
│   ├── .env                       # Secrets & DB URL
│
├── mobile/
│   └── geofence_client/           # Flutter mobile app (optional)
│
├── docker-compose.yml             # MySQL + Redis for instalation
├── README.md                      # You are here

⚙️ Installation
1. Clone the Repository
git clone https://github.com/yourname/geofence-app.git
cd geofence-app

2. Backend Setup (WSL / Ubuntu)
Install virtual environment
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

3. Start MySQL & Redis (Docker)
docker compose up -d

4. Apply DB models automatically

The first run of FastAPI will run SQLAlchemy create_all().

🔑 Configuration

Create backend/.env:

DATABASE_URL=mysql+pymysql://root:password@localhost:3306/geofence_db
REDIS_URL=redis://localhost:6379/0

# Firebase service account file (must be present in backend folder)
FCM_SERVICE_ACCOUNT_FILE=firebase-service-account.json


Add your Firebase service account JSON file:

backend/firebase-service-account.json

▶️ Running the System
1. Start FastAPI
cd backend
source venv/bin/activate
uvicorn app.main:app --reload


Docs available at:
👉 http://127.0.0.1:8000/docs

2. Start Celery Worker

Open a second terminal:

cd backend
source venv/bin/activate
celery -A app.celery_app:celery_app worker -l info

3. Start Mobile App (Windows)
cd mobile/geofence_client
flutter run

🔌 API Endpoints
Users
POST /users/
GET  /users/{id}
GET  /users/{id}/profile

Geofences
POST /geofences/

Device Registration
POST /devices/register

Location Updates
POST /location/update


Returns:

{
  "inside": false,
  "distance_m": 7963.8,
  "alert": true
}

Alerts
GET /alerts/
GET /users/{id}/alerts

🧪 Testing Workflow
1. Create user
POST /users/
{ "username": "anand-test" }

2. Create geofence
POST /geofences/
{
  "user_id": 1,
  "center_lat": 40.73,
  "center_lon": -73.93,
  "radius_m": 1000
}

3. Register device
POST /devices/register
{
  "user_id": 1,
  "platform": "android",
  "fcm_token": "<real token from Flutter app>"
}

4. Send outside location
POST /location/update
{
  "user_id": 1,
  "lat": 40.8000,
  "lon": -73.9500
}

5. Check alerts
GET /alerts/

🛠️ Troubleshooting
Celery not processing tasks?

Confirm Redis is running:
docker ps

Ensure Celery terminal is open

Check .env contains correct REDIS_URL

FCM errors

Common causes:
✔ Wrong or fake token
✔ Incorrect service account
✔ Missing FCM API enabled

Flutter cannot reach backend

Use:

10.0.2.2:8000 (Android emulator)

Local PC LAN IP (real device)

🔮 Future Enhancements

Polygon geofences

Multi-user or group geofences

Web dashboard (React/Vue)

Threat / weather integration

Real-time tracking with WebSockets

Kafka for event streaming ( For future)

PostGIS for advanced geo-calculations (can replace mysql)



cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

docker compose up -d

cd backend
source venv/bin/activate
uvicorn app.main:app --reload




cd backend
source venv/bin/activate
celery -A app.celery_app:celery_app worker -l info



http://127.0.0.1:8000/docs


Testing Workflow
1. Create user
POST /users/
{ "username": "anand-test" }

2. Create geofence
POST /geofences/
{
  "user_id": 1,
  "center_lat": 40.73,
  "center_lon": -73.93,
  "radius_m": 1000
}

3. Register device
POST /devices/register
{
  "user_id": 1,
  "platform": "android",
  "fcm_token": "<real token from Flutter app>"
}

4. Send outside location
POST /location/update
{
  "user_id": 1,
  "lat": 40.8000,
  "lon": -73.9500
}

5. Check alerts
GET /alerts/
