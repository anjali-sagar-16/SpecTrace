# SpecTrace Backend

FastAPI backend, PostgreSQL database, and authentication services for **SpecTrace: AI-Powered Software Change Intelligence Platform**.

## Project Architecture

```text
backend/
├── app/
│   ├── api/
│   │   ├── deps.py               # Reusable dependencies (get_current_user, HTTPBearer)
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── auth.py       # Auth routes: /register, /login, /me
│   │       │   ├── health.py     # Health routes: /health, /health/db
│   │       │   ├── projects.py   # Protected Project CRUD endpoints
│   │       │   └── repositories.py # Protected Repository CRUD endpoints
│   │       └── api.py            # API v1 router aggregator
│   ├── core/
│   │   ├── config.py             # Pydantic BaseSettings, JWT, DB & CORS config
│   │   └── security.py           # Argon2 hashing (pwdlib) & PyJWT token utilities
│   ├── db/
│   │   ├── base.py               # SQLAlchemy declarative Base
│   │   ├── init_db.py            # Development schema init & relationship verification
│   │   └── session.py            # SQLAlchemy 2.x engine, connection pool & get_db
│   ├── models/
│   │   ├── user.py               # User model (users table)
│   │   ├── project.py            # Project model (projects table with user cascade)
│   │   └── repository.py         # Repository model (repositories table with project cascade)
│   ├── schemas/
│   │   ├── user.py               # User registration, login, and safe profile schemas
│   │   ├── project.py            # Project creation, update, and response schemas
│   │   └── repository.py         # Repository creation and response schemas
│   └── main.py                   # FastAPI application entry point & CORS configuration
├── tests/
│   ├── test_security.py          # Argon2 hashing & verification unit tests
│   ├── test_auth.py              # User registration endpoint tests
│   ├── test_login.py             # Login, JWT issuing, and /me access tests
│   ├── test_projects.py          # Project CRUD and ownership isolation tests
│   └── test_repositories.py      # Repository CRUD and cross-project isolation tests
├── docker-compose.yml            # PostgreSQL 16 container with persistent volume
├── .env.example                  # Environment configuration template
├── requirements.txt              # Production and testing dependencies
└── README.md                     # Backend documentation
```

## Setup & Installation

### 1. Prerequisites
- Python 3.12 or 3.13 (recommended; pre-built binary wheels available).
- Docker Desktop or Docker Engine with Docker Compose.

### 2. Create Virtual Environment
```powershell
# Windows
py -3.13 -m venv .venv
.\.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```
*(The `.env` file is excluded from Git to prevent secret leakage).*

---

## Database Management (Docker Compose)

### Start PostgreSQL
Run from the `backend/` directory:
```bash
docker compose up -d
```
Starts `spectrace-db` (`postgres:16-alpine`) on port `5432` with persistent volume `spectrace_pgdata`.

### Verify Container Status
```bash
docker compose ps
```

### Stop PostgreSQL (Preserving Data)
```bash
docker compose down
```

---

## Running the Application

Start the development server with live reload:
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

---

## Implemented API Endpoints (Phase 2)

### Health Check Endpoints
- `GET /api/v1/health` — Service operational status and metadata.
- `GET /api/v1/health/db` — PostgreSQL database connectivity verification.

### Authentication Endpoints
- `POST /api/v1/auth/register` — Register a new user with Argon2 password hashing (`201 Created`).
- `POST /api/v1/auth/login` — Authenticate credentials and receive a signed JWT access token (`200 OK`).
- `GET /api/v1/auth/me` — Protected endpoint returning the authenticated user's safe profile (`200 OK`).

### Project CRUD Endpoints (Protected)
- `POST /api/v1/projects` — Create a project bound to the authenticated user (`201 Created`).
- `GET /api/v1/projects` — List all projects owned exclusively by the caller (`200 OK`).
- `GET /api/v1/projects/{project_id}` — Get project details; returns `404` if not owned (`200 OK`).
- `PATCH /api/v1/projects/{project_id}` — Update name or description; rejects `owner_id` modification (`200 OK`).
- `DELETE /api/v1/projects/{project_id}` — Delete project and cascade-delete attached repositories (`200 OK`).

### Repository CRUD Endpoints (Protected)
- `POST /api/v1/projects/{project_id}/repositories` — Add code repository metadata to a project (`201 Created`).
- `GET /api/v1/projects/{project_id}/repositories` — List repositories for an owned project (`200 OK`).
- `GET /api/v1/projects/{project_id}/repositories/{repository_id}` — Get repository details; verifies ownership and project matching (`200 OK`).
- `DELETE /api/v1/projects/{project_id}/repositories/{repository_id}` — Remove repository from project (`200 OK`).

---

## Running Automated Tests

Run the complete test suite with `unittest`:

```powershell
# Windows
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v

# macOS / Linux
python -m unittest discover -s tests -p "test_*.py" -v
```

---

## Roadmap & Upcoming Features

- **Phase 3: GitHub Integration**: OAuth app flow, webhook ingestion, AST parser, and repository tree indexing.
- **Phase 4: AI & RAG Engine**: Requirement change parsing, vector embeddings, graph tracing, and blast-radius impact analysis.
