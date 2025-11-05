from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_preferences_roundtrip():
    payload = {
        "channels": ["email", "push"],
        "digest": True,
        "quiet_hours": {"start": "22:00", "end": "07:00"},
    }
    user_id = "u1"

    r = client.put(f"/users/{user_id}/preferences", json=payload)
    assert r.status_code == 200

    r = client.get(f"/users/{user_id}/preferences")
    assert r.status_code == 200
    data = r.json()
    assert set(data["channels"]) == {"email", "push"}
    assert data["digest"] is True
