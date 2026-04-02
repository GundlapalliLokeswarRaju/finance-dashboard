from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import Base, engine
from app.routers import auth, dashboard, transactions, users

# ── Create all DB tables on startup ─────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ── App instance ─────────────────────────────────────────────────────────────
app = FastAPI(
    title="Finance Dashboard API",
    description=(
        "A role-based finance management backend built with FastAPI + SQLite.\n\n"
        "## Roles\n"
        "| Role     | Permissions |\n"
        "|----------|-------------|\n"
        "| `admin`  | Full access: manage users, create/update/delete records |\n"
        "| `analyst`| Read transactions, view dashboard summaries |\n"
        "| `viewer` | Read-only access to own profile |\n\n"
        "## Quick Start\n"
        "1. `POST /auth/login` with admin credentials to get a JWT token\n"
        "2. Click **Authorize** and paste the token\n"
        "3. Explore all endpoints below"
    ),
    version="1.0.0",
    contact={"name": "Finance Dashboard"},
    license_info={"name": "MIT"},
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global exception handler ─────────────────────────────────────────────────
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again."},
    )


# ── Register routers ──────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(transactions.router)
app.include_router(dashboard.router)


# ── Health check ─────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"], summary="Health check")
def health_check():
    return {"status": "ok", "message": "Finance Dashboard API is running"}


@app.get("/", tags=["Health"], include_in_schema=False)
def root():
    return {"message": "Visit /docs for the interactive API documentation"}
