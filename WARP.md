# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Common commands

- Setup (local Python, with venv)
  ```sh
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  python -m pip install -r requirements.txt
  ```
  - Deactivate: `deactivate`
- Run (local dev)
  ```sh
  uvicorn app.main:app --reload
  ```
  - API docs: http://localhost:8000/docs
  - Health check: http://localhost:8000/health
  - Optional env: `SERVICE_NAME` and `SERVICE_VERSION` influence FastAPI title/version.
- Windows (PowerShell) env vars
  ```pwsh
  $env:SERVICE_NAME = 'notification-hub'
  $env:SERVICE_VERSION = '0.1.0'
  uvicorn app.main:app --reload
  ```
  - Unset later (optional):
    ```pwsh
    Remove-Item Env:SERVICE_NAME, Env:SERVICE_VERSION -ErrorAction Ignore
    ```
- Tests
  ```sh
  pytest -q
  ```
  - Run a single test:
    ```sh
    pytest tests/test_health.py::test_health -q
    ```
    or by keyword:
    ```sh
    pytest -k preferences -q
    ```
- Docker
  ```sh
  docker build -t notification-hub .
  docker run -p 8000:8000 notification-hub
  ```
- Docker Compose
  ```sh
  docker compose up --build
  ```
- Linting/formatting
  - No linter/formatter is configured in this repo.

## Architecture overview

High-level design: a small FastAPI microservice that manages per-user notification preferences and accepts notification send requests. Persistence is in-memory only.

- Web API (`app/main.py`)
  - Creates a FastAPI app whose `title` and `version` derive from `SERVICE_NAME` and `SERVICE_VERSION` env vars (defaulting to `notification-hub` and `0.1.0`).
  - Endpoints:
    - `GET /health` – liveness probe returning `{ "status": "ok" }`.
    - `GET /` – service metadata: title, version, and docs link.
    - `GET /users/{user_id}/preferences` – returns a user’s `Preference`. If none exists, initializes a default (`channels=[email]`, `digest=False`).
    - `PUT /users/{user_id}/preferences` – upserts a user’s `Preference`.
    - `POST /notifications` – accepts a `Notification`, resolves delivery channels (explicit on request > stored preference > default `[email]`), appends to store, and returns an acceptance payload; no external delivery is performed.
  - Response/validation models are Pydantic `BaseModel` types.

- Domain models (`app/models.py`)
  - `DeliveryChannel` enum: `email | sms | push | webhook`.
  - `Preference`: `channels: List[DeliveryChannel]`, `digest: bool`, optional `quiet_hours` window.
  - `Notification`: `user_id`, `title`, `body`, optional `channels` override.

- Storage (`app/storage.py`)
  - `InMemoryStore` with an `RLock` guards a dict of user preferences and an in-memory list of notifications.
  - Methods: `get_prefs`, `set_prefs`, `add_notification`, `list_notifications`.
  - A module-level singleton `STORE` is imported by the API layer.

- Tests (`tests/test_health.py`)
  - Uses `fastapi.testclient.TestClient` for API tests.
  - Covers health endpoint and a round-trip preference set/get.

- Containerization & orchestration
  - `Dockerfile`: Python 3.11 slim image, installs `requirements.txt`, runs `uvicorn app.main:app` on port 8000.
  - `docker-compose.yml`: single service `notification-hub:dev`, maps `8000:8000`, sets `SERVICE_NAME`/`SERVICE_VERSION` env.

- CI/CD (GitHub Actions)
  - Workflow `.github/workflows/ci.yml`:
    - `test` job: Python 3.11, installs `requirements.txt`, runs `pytest -q` on PRs and pushes to `main`.
    - `build-and-push` job: on non-PR pushes/tags, builds image with Buildx and pushes to GHCR at `ghcr.io/<owner>/notification-hub` with tags: `latest` (for `main`), `sha-<commit>`, and any Git tag value.
