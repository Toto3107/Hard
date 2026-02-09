
# RaKsh Borewell Decision Support Backend

RaKsh is a backend service that predicts **borewell feasibility and depth** for a given location, stores predictions per user, and lets you record actual drilling outcomes later. It is built with **FastAPI**, **PostgreSQL**, **Docker**, and a trained **ML model**. [web:191][web:192]

---

## Features

- User registration and login with **JWT-based** authentication. [web:133][web:165]
- ML-powered prediction of:
  - Borewell feasibility (boolean).
  - Expected drilling depth (meters).
- Storage of predictions in PostgreSQL per authenticated user.
- Ability to record **actual feasibility and depth** after drilling, enabling feedback and model evaluation.
- Containerized stack (API + DB) using Docker Compose. [web:158][web:193]

---

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL 16
- **ML**: scikit-learn models serialized with joblib
- **Auth**: JWT (OAuth2 password flow)
- **Containerization**: Docker & Docker Compose

---

## Project Structure

```text
raksh-bb/
├── app/
│   ├── main.py
│   ├── db.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth_utils.py
│   ├── ml_models.py
│   └── routers/
│       ├── auth.py
│       ├── predict.py
│       └── borewells.py
├── models/
│   ├── feasibility_model.joblib
│   └── depth_model.joblib
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env
└── README.md
```

- `app/main.py`: FastAPI app, router registration, DB init, model loading.
- `app/models.py`: SQLAlchemy models for `User` and `Borewell`.
- `app/schemas.py`: Pydantic models for requests/responses.
- `app/auth_utils.py`: Password hashing and JWT helpers.
- `app/ml_models.py`: Loads serialized ML models and exposes `predict_from_models`.
- `app/routers/`:
  - `auth.py`: `/auth/register`, `/auth/login`, `get_current_user`.
  - `predict.py`: `/predict/` inference endpoint.
  - `borewells.py`: CRUD-style endpoints for borewell predictions & outcomes.
- `models/`: Trained scikit-learn models used for inference. [web:166][web:185]

---

## Prerequisites

- Docker and Docker Compose installed and running. [web:158][web:194]
- (Optional) Python 3.11+ and virtualenv if you want to run locally without Docker.

---

## Environment configuration

Create a `.env` file in the project root:

```env
# Database
POSTGRES_DB=raksh_db
POSTGRES_USER=raksh_user
POSTGRES_PASSWORD=raksh_password
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Auth
SECRET_KEY=change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

These values are used by the API and Docker Compose to connect to Postgres and sign JWTs. [web:151][web:193]

---

## Running with Docker

From the project root (`raksh-bb/`):

```bash
docker compose up --build
```

This will:

- Start a PostgreSQL 16 container.
- Build the FastAPI image, install `requirements.txt`, and start Uvicorn.
- Run DB migrations/table creation on startup and load ML models. [web:158]

Once running:

- API base: `http://localhost:8000`
- Interactive docs (Swagger UI): `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

To stop:

```bash
docker compose down
```

---

## Running locally without Docker (optional)

If you want to run just the API on your host:

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Make sure a Postgres instance is running and `.env` points to it. [web:192][web:197]

---

## API Overview

### Health

- `GET /health`  
  Returns a simple status JSON to verify the service is up.

---

### Auth

#### Register

- `POST /auth/register`
- Body (JSON):

```json
{
  "email": "user@example.com",
  "password": "strong password here",
  "full_name": "Example User"
}
```

- Response (201):

```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "Example User",
  "is_active": true
}
```

#### Login (JWT)

- `POST /auth/login`
- Body type: `application/x-www-form-urlencoded` (OAuth2 password flow). [web:133][web:162]

Fields:

- `username`: email used at registration.
- `password`: user password.

- Response (200):

```json
{
  "access_token": "<jwt-token>",
  "token_type": "bearer"
}
```

Use this token in the `Authorization` header:

```http
Authorization: Bearer <jwt-token>
```

---

### ML Prediction

#### Predict borewell feasibility & depth

- `POST /predict/`
- Body (JSON):

```json
{
  "latitude": 23.2599,
  "longitude": 77.4126
}
```

- Response (200):

```json
{
  "latitude": 23.2599,
  "longitude": 77.4126,
  "predicted_feasible": false,
  "predicted_depth_m": 0.0,
  "model_version": "v1.0-rf"
}
```

This endpoint **does not require auth** (unless you choose to enforce it). [web:166][web:185]

---

### Borewell records (JWT protected)

All borewell endpoints require:

```http
Authorization: Bearer <jwt-token>
```

#### Create and store a borewell prediction

- `POST /borewells/`
- Body (JSON):

```json
{
  "latitude": 23.2599,
  "longitude": 77.4126
}
```

- Response (201):

```json
{
  "id": 1,
  "latitude": 23.2599,
  "longitude": 77.4126,
  "predicted_feasible": false,
  "predicted_depth_m": 0.0,
  "model_version": "v1.0-rf",
  "actual_feasible": null,
  "actual_depth_m": null
}
```

The prediction is computed via the ML model and stored in Postgres for the current user.

#### List current user’s borewells

- `GET /borewells/`
- Response (200): list of borewell records for the authenticated user (most recent first).

Example:

```json
[
  {
    "id": 1,
    "latitude": 23.2599,
    "longitude": 77.4126,
    "predicted_feasible": false,
    "predicted_depth_m": 0.0,
    "model_version": "v1.0-rf",
    "actual_feasible": true,
    "actual_depth_m": 110.0
  }
]
```

#### Get one borewell (optional, if implemented)

- `GET /borewells/{id}`  
  Returns the borewell for that `id` if it belongs to the current user.

#### Update actual outcome

- `PATCH /borewells/{id}/outcome`
- Body (JSON):

```json
{
  "actual_feasible": true,
  "actual_depth_m": 110.0
}
```

- Response (200): the updated borewell record.

This allows you to log **real-world results** and later compute metrics like accuracy and error. [web:181][web:184]

---

## Development Notes

- **ML model versions**: `MODEL_VERSION` is tracked in `ml_models.py` and stored with each prediction. Update it when retraining. [web:173][web:185]
- **Security**:
  - Passwords hashed with passlib + bcrypt in `auth_utils.py`.
  - JWT tokens signed with `SECRET_KEY` and expiry configured via env. [web:133][web:165]
- **Database migrations**:
  - Current setup creates tables via SQLAlchemy metadata on startup.
  - For a larger project, integrate Alembic.

---

## Future Work

This backend is ready for:

- A **real-time data scraper** to feed new borewell data.
- A **retraining pipeline** that updates the ML models and `MODEL_VERSION`.
- Monitoring dashboards/notebooks for model performance over time. [web:181][web:178]


