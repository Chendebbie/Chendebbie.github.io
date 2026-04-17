# User Membership System

A production-ready **FastAPI** backend implementing a full User Membership System with JWT authentication, OAuth2 scopes, async PostgreSQL, and Docker support.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI (async) |
| Database | PostgreSQL 16 via SQLAlchemy 2.0 (asyncpg) |
| Migrations | Alembic |
| Security | JWT (python-jose), bcrypt (passlib), OAuth2 scopes |
| Config | pydantic-settings |
| Container | Docker + docker-compose |

---

## Project Structure

```
.
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── auth.py      # /auth routes: login, register, refresh
│   │       │   └── users.py     # /users routes: profile + admin CRUD
│   │       └── router.py        # Aggregates all v1 routers
│   ├── core/
│   │   ├── config.py            # App settings via pydantic-settings
│   │   ├── security.py          # JWT creation/decoding, password hashing
│   │   └── deps.py              # FastAPI dependency injections
│   ├── db/
│   │   ├── base.py              # SQLAlchemy DeclarativeBase
│   │   └── session.py           # Async engine + session factory
│   ├── models/
│   │   └── user.py              # SQLAlchemy User model
│   └── schemas/
│       ├── token.py             # Token + TokenPayload Pydantic schemas
│       └── user.py              # User Pydantic schemas (create/read/update)
├── alembic/                     # Alembic migration environment
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── alembic.ini
├── main.py                      # FastAPI application entry point
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

---

## Quick Start with Docker

### 1. Clone and configure environment

```bash
git clone <your-repo-url>
cd <repo-directory>
cp .env.example .env
```

Edit `.env` and set a strong `SECRET_KEY` and `POSTGRES_PASSWORD`:

```bash
# Generate a secure secret key
openssl rand -hex 32
```

### 2. Build and start all services

```bash
docker-compose up --build
```

This will:
1. Start a **PostgreSQL 16** database container.
2. Wait until the database is healthy.
3. Run **Alembic** migrations automatically (`alembic upgrade head`).
4. Start the **FastAPI** application on port `8000`.

### 3. Access the API

| URL | Description |
|---|---|
| http://localhost:8000/docs | Interactive Swagger UI |
| http://localhost:8000/redoc | ReDoc documentation |
| http://localhost:8000/health | Health check endpoint |

---

## Running Without Docker (Local Development)

### Prerequisites
- Python 3.12+
- PostgreSQL 16 running locally

### Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Edit .env to point POSTGRES_SERVER=localhost

# Apply database migrations
alembic upgrade head

# Start the development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## API Endpoints

### Auth (`/api/v1/auth`)

| Method | Path | Description |
|---|---|---|
| `POST` | `/register` | Create a new user account |
| `POST` | `/login` | Obtain access + refresh JWT tokens |
| `POST` | `/refresh` | Exchange a refresh token for a new access token |

### Users (`/api/v1/users`)

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/me` | `me` scope | Get current user profile |
| `PUT` | `/me` | `me` scope | Update current user profile |
| `GET` | `/` | `admin` scope | List all users (admin only) |
| `GET` | `/{user_id}` | `admin` scope | Get user by ID (admin only) |
| `PUT` | `/{user_id}` | `admin` scope | Update any user (admin only) |
| `DELETE` | `/{user_id}` | `admin` scope | Delete a user (admin only) |

---

## OAuth2 Scopes

| Scope | Description |
|---|---|
| `me` | Read/update own profile |
| `users:read` | Read all users |
| `users:write` | Create or update users |
| `admin` | Full administrative access |

When logging in via `/api/v1/auth/login`, include the desired scopes in the `scope` field of the OAuth2 form.

---

## Database Migrations

```bash
# Auto-generate a new migration after model changes
alembic revision --autogenerate -m "describe your change"

# Apply all pending migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1
```

---

## Environment Variables Reference

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | *(required)* | JWT signing secret — use `openssl rand -hex 32` |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token lifetime in minutes |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token lifetime in days |
| `POSTGRES_SERVER` | *(required)* | Hostname/IP of PostgreSQL server |
| `POSTGRES_PORT` | `5432` | PostgreSQL port |
| `POSTGRES_USER` | *(required)* | PostgreSQL username |
| `POSTGRES_PASSWORD` | *(required)* | PostgreSQL password |
| `POSTGRES_DB` | *(required)* | PostgreSQL database name |
| `BACKEND_CORS_ORIGINS` | `[]` | JSON array of allowed CORS origins |

---

## Security Notes

- Passwords are hashed with **bcrypt** via `passlib`.
- JWT tokens are signed with **HS256** (configurable via `ALGORITHM`).
- The Docker image runs as a **non-root user** (`appuser`).
- Refresh tokens are separate short-lived tokens that cannot be used for API access directly.
- Always rotate `SECRET_KEY` in production and store it securely (e.g., in a secrets manager).
