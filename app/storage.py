from threading import RLock
from typing import Dict, List, Optional

from .models import Preference, Notification


class InMemoryStore:
    def __init__(self) -> None:
        self._prefs: Dict[str, Preference] = {}
        self._notifications: List[Notification] = []
        self._lock = RLock()

    def get_prefs(self, user_id: str) -> Optional[Preference]:
        with self._lock:
            return self._prefs.get(user_id)

    def set_prefs(self, user_id: str, prefs: Preference) -> Preference:
        with self._lock:
            self._prefs[user_id] = prefs
            return prefs

    def add_notification(self, notif: Notification) -> None:
        with self._lock:
            self._notifications.append(notif)

    def list_notifications(self) -> List[Notification]:
        with self._lock:
            return list(self._notifications)


STORE = InMemoryStore()
