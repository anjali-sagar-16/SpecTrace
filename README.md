# SpecTrace

**SpecTrace** is an AI-powered Software Change Intelligence Platform designed to help engineering teams understand how changing software requirements affect their codebase before writing code.

---

## Architecture Overview

```text
SpecTrace/
├── frontend/               # React + Vite frontend application
│   ├── src/
│   │   ├── components/
│   │   │   ├── auth/       # Login and Registration components
│   │   │   └── dashboard/  # SaaS Dashboard (Overview, Projects, Repositories, Requirements, Impact Analysis)
│   │   └── App.jsx         # Client-side router and state management
├── backend/                # Python FastAPI backend service
│   ├── app/
│   │   ├── api/            # API v1 routers and dependency injection
│   │   ├── core/           # Security (Argon2, PyJWT) and App Settings
│   │   ├── db/             # SQLAlchemy 2.x session and Base models
│   │   ├── models/         # User, Project, and Repository database entities
│   │   └── schemas/        # Pydantic v2 validation models
│   ├── tests/              # 38 automated integration and unit tests
│   └── docker-compose.yml  # PostgreSQL 16 container definition
└── docs/                   # System design, architecture, and development status
```

---

## Tech Stack

- **Frontend**: React 19, JavaScript, Vite, CSS Modules / Pure CSS
- **Backend**: FastAPI 0.115, Python 3.13, Pydantic v2
- **Database & ORM**: PostgreSQL 16 (Alpine), SQLAlchemy 2.0, psycopg 3
- **Security**: Argon2 password hashing (`pwdlib[argon2]`), PyJWT (HS256)
- **Infrastructure**: Docker Compose, Virtual Environments

---

## Development Milestones

### Phase 1: Frontend Foundation (Completed)
- React 19 + Vite setup with hot module reloading.
- Professional authentication UI: Login, Sign-up, validation, and show/hide password controls.
- Full SaaS Developer Dashboard: Overview metrics, Projects view, Repositories view, Requirements manager, Impact Analysis visualizer, and History feed.
- GitHub connection modal interface.

### Phase 2: Backend Foundation & Core APIs (Completed)
- Scalable FastAPI backend with structured layered architecture.
- PostgreSQL 16 Docker container with persistent volume storage.
- SQLAlchemy 2.x connection pooling, declarative models, and relational schema migrations.
- **User Model & Authentication**:
  - Secure Argon2 password hashing via `pwdlib[argon2]` (rejects plain text and leaks).
  - User registration (`POST /api/v1/auth/register`) with input sanitization and duplicate rejection.
  - User login (`POST /api/v1/auth/login`) issuing signed JWT access tokens.
  - Protected profile inspection (`GET /api/v1/auth/me`).
- **Protected Project CRUD**:
  - Create, read, update, and delete projects (`/api/v1/projects`).
  - Strict ownership isolation (cross-user access returns `404 Not Found`).
- **Protected Repository CRUD**:
  - Add, list, fetch, and delete code repository records (`/api/v1/projects/{project_id}/repositories`).
  - Enforced project-to-repository association and owner verification.
- **Automated Test Suite**: 38 comprehensive automated tests covering security, authentication, and CRUD isolation.

---

## Roadmap (Future Phases)

- **Phase 3: GitHub Integration**: GitHub App OAuth, Webhooks, repository synchronization, and AST code indexing.
- **Phase 4: AI & RAG Change Intelligence**: Requirement parsing, vector embeddings, graph tracing, and blast-radius impact analysis.
- **Phase 5: End-to-End Integration**: Connecting React frontend to FastAPI endpoints with persistent token management.
