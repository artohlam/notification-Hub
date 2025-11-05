# Notification Hub

A FastAPI microservice for centralized notification preferences and routing.

Quickstart
- Local (Python):
  - python -m pip install -r requirements.txt
  - uvicorn app.main:app --reload
- Docker:
  - docker build -t notification-hub .
  - docker run -p 8000:8000 notification-hub
- Compose:
  - docker compose up --build

API
- Docs: http://localhost:8000/docs
- Health: GET /health
- Preferences:
  - GET /users/{user_id}/preferences
  - PUT /users/{user_id}/preferences
- Send notification: POST /notifications

CI/CD
GitHub Actions workflow builds/tests on PRs and on push to main builds and pushes a container image to GHCR at:
- ghcr.io/${{ github.repository_owner }}/notification-hub

Set SERVICE_NAME and SERVICE_VERSION via env if desired.
