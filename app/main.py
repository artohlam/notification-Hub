import os
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

from .models import Preference, Notification, DeliveryChannel
from .storage import STORE


class SendResponse(BaseModel):
    user_id: str
    channels: List[DeliveryChannel]
    accepted: bool = True


app = FastAPI(
    title=os.getenv("SERVICE_NAME", "notification-hub"),
    version=os.getenv("SERVICE_VERSION", "0.1.0"),
    description=(
        "Personalized notification hub microservice. "
        "Manage user notification preferences and route notifications."
    ),
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/")
def root() -> dict:
    return {"service": app.title, "version": app.version, "docs": "/docs"}


@app.get("/users/{user_id}/preferences", response_model=Preference)
def get_prefs(user_id: str) -> Preference:
    prefs = STORE.get_prefs(user_id)
    if not prefs:
        prefs = Preference(channels=[DeliveryChannel.email], digest=False)
        STORE.set_prefs(user_id, prefs)
    return prefs


@app.put("/users/{user_id}/preferences", response_model=Preference)
def set_prefs(user_id: str, prefs: Preference) -> Preference:
    STORE.set_prefs(user_id, prefs)
    return prefs


@app.post("/notifications", response_model=SendResponse)
def send_notification(notif: Notification) -> SendResponse:
    prefs = STORE.get_prefs(notif.user_id)
    channels = notif.channels or (prefs.channels if prefs else [DeliveryChannel.email])
    STORE.add_notification(notif)
    return SendResponse(user_id=notif.user_id, channels=channels, accepted=True)
