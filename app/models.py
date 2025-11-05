from enum import Enum
from typing import List, Optional
from datetime import time

from pydantic import BaseModel


class DeliveryChannel(str, Enum):
    email = "email"
    sms = "sms"
    push = "push"
    webhook = "webhook"


class QuietHours(BaseModel):
    start: time
    end: time


class Preference(BaseModel):
    channels: List[DeliveryChannel] = []
    digest: bool = False
    quiet_hours: Optional[QuietHours] = None


class Notification(BaseModel):
    user_id: str
    title: str
    body: str
    channels: Optional[List[DeliveryChannel]] = None
