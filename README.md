# 💰 Finance Dashboard API

A role-based finance management backend built with **FastAPI**, **SQLAlchemy**, and **SQLite**. Designed for a finance dashboard system where users interact with financial records based on their assigned role.

---

## 📋 Table of Contents

- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Architecture & Design Decisions](#architecture--design-decisions)
- [Role-Based Access Control](#role-based-access-control)
- [Data Models](#data-models)
- [API Reference](#api-reference)
- [Setup & Installation](#setup--installation)
- [Running the Server](#running-the-server)
- [Testing the API](#testing-the-api)
- [Assumptions & Tradeoffs](#assumptions--tradeoffs)
- [Optional Enhancements Implemented](#optional-enhancements-implemented)

---

## 🛠 Tech Stack

| Layer        | Technology                        |
|--------------|-----------------------------------|
| Framework    | FastAPI 0.111                     |
| ORM          | SQLAlchemy 2.0                    |
| Database     | SQLite (via `finance.db` file)    |
| Auth         | JWT (python-jose) + bcrypt        |
| Validation   | Pydantic v2                       |
| Server       | Uvicorn (ASGI)                    |
| Language     | Python 3.10+                      |

---

## 📁 Project Structure

```
finance-dashboard/
├── .env                        # Environment config (JWT secret, DB URL)
├── requirements.txt            # Python dependencies
├── seed.py                     # DB seed script (users + sample transactions)
└── app/
    ├── main.py                 # App entry point, router registration, CORS
    ├── database.py             # SQLAlchemy engine + session + Base
    ├── core/
    │   ├── config.py           # App settings via pydantic-settings
    │   ├── security.py         # Password hashing + JWT encode/decode
    │   └── dependencies.py     # FastAPI deps: get_current_user, require_roles()
    ├── models/
    │   ├── user.py             # User ORM model + UserRole enum
    │   └── transaction.py      # Transaction ORM model + TransactionType enum
    ├── schemas/
    │   ├── user.py             # Request/response Pydantic schemas for users
    │   └── transaction.py      # Schemas for transactions, filters, dashboard
    ├── services/
    │   ├── auth.py             # Login / token creation logic
    │   ├── user.py             # User CRUD business logic
    │   ├── transaction.py      # Transaction CRUD + filtering + pagination
    │   └── dashboard.py        # Aggregation logic for dashboard summary
    └── routers/
        ├── auth.py             # POST /auth/login
        ├── users.py            # /users/* endpoints
        ├── transactions.py     # /transactions/* endpoints
        └── dashboard.py        # /dashboard/summary endpoint
```

---

## 🏗 Architecture & Design Decisions

### Separation of Concerns
The codebase follows a strict three-layer architecture:

```
Router (HTTP layer)
    ↓  validates request shape via Pydantic schemas
Service (Business logic layer)
    ↓  applies business rules, raises domain errors
Model (Data layer)
    ↓  maps to SQLite tables via SQLAlchemy ORM
```

Routers never talk to models directly — all logic lives in services. This keeps routes thin, testable, and readable.

### Authentication
JWT-based stateless authentication. On login, the server issues a signed token containing the user's `id` and `role`. Every protected endpoint validates this token via the `get_current_user` dependency.

### Access Control
Role enforcement is implemented as a **dependency factory** (`require_roles()`). Each endpoint declares exactly which roles are permitted:

```python
# Example: only admins can create users
@router.post("/")
def create_user(_: User = Depends(require_admin)):
    ...

# Analysts and admins can view dashboard
@router.get("/summary")
def dashboard(_: User = Depends(require_analyst_or_above)):
    ...
```

This means access rules are co-located with routes — easy to audit and change.

### Soft Deletes
Transactions are never hard-deleted. Instead, they have an `is_deleted` flag. All queries filter `is_deleted == 0` by default. This preserves audit history.

### Error Handling
- Pydantic validates all incoming request bodies and query params automatically
- Services raise `HTTPException` with descriptive messages and correct status codes
- A global exception handler catches any unhandled errors and returns a safe 500 response

---

## 🔐 Role-Based Access Control

Three roles are supported:

| Role       | Description                                          |
|------------|------------------------------------------------------|
| `admin`    | Full access: manage users, create/modify/delete records |
| `analyst`  | Read transactions, view dashboard summaries          |
| `viewer`   | Can only view their own profile (`/users/me`)        |

### Permission Matrix

| Endpoint                          | Viewer | Analyst | Admin |
|-----------------------------------|--------|---------|-------|
| `POST   /auth/login`              | ✅     | ✅      | ✅    |
| `GET    /users/me`                | ✅     | ✅      | ✅    |
| `GET    /users/`                  | ❌     | ❌      | ✅    |
| `POST   /users/`                  | ❌     | ❌      | ✅    |
| `GET    /users/{id}`              | ❌     | ❌      | ✅    |
| `PATCH  /users/{id}`              | ❌     | ❌      | ✅    |
| `DELETE /users/{id}`              | ❌     | ❌      | ✅    |
| `GET    /transactions/`           | ❌     | ✅      | ✅    |
| `GET    /transactions/{id}`       | ❌     | ✅      | ✅    |
| `POST   /transactions/`           | ❌     | ❌      | ✅    |
| `PATCH  /transactions/{id}`       | ❌     | ❌      | ✅    |
| `DELETE /transactions/{id}`       | ❌     | ❌      | ✅    |
| `GET    /dashboard/summary`       | ❌     | ✅      | ✅    |

---

## 🗄 Data Models

### User

| Field            | Type     | Notes                              |
|------------------|----------|------------------------------------|
| `id`             | Integer  | Primary key                        |
| `full_name`      | String   | Required                           |
| `email`          | String   | Unique, indexed                    |
| `hashed_password`| String   | bcrypt hashed                      |
| `role`           | Enum     | `admin` / `analyst` / `viewer`     |
| `is_active`      | Boolean  | Inactive users cannot log in       |
| `created_at`     | DateTime | Auto-set on creation               |
| `updated_at`     | DateTime | Auto-updated on change             |

### Transaction

| Field        | Type     | Notes                                   |
|--------------|----------|-----------------------------------------|
| `id`         | Integer  | Primary key                             |
| `amount`     | Float    | Must be > 0, rounded to 2 decimal places|
| `type`       | Enum     | `income` or `expense`                   |
| `category`   | String   | e.g. Salary, Rent, Groceries            |
| `date`       | Date     | The transaction date (YYYY-MM-DD)       |
| `notes`      | Text     | Optional description                    |
| `is_deleted` | Integer  | Soft delete flag (0=active, 1=deleted)  |
| `created_by` | FK(User) | Admin who created this record           |
| `created_at` | DateTime | Auto-set on creation                    |
| `updated_at` | DateTime | Auto-updated on change                  |

---

## 📡 API Reference

### Authentication

#### `POST /auth/login`
Get a JWT access token.

**Request:**
```json
{
  "email": "admin@finance.com",
  "password": "admin123"
}
```

**Response `200`:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### Users

> All `/users/*` endpoints except `/users/me` require **Admin** role.

#### `POST /users/` — Create user
```json
{
  "full_name": "Jane Doe",
  "email": "jane@example.com",
  "password": "secure123",
  "role": "analyst"
}
```

#### `GET /users/` — List all users
Returns `{ total, users[] }` with all registered users.

#### `GET /users/me` — Current user profile
Returns the authenticated user's profile. Available to all roles.

#### `GET /users/{id}` — Get user by ID

#### `PATCH /users/{id}` — Update role or status
```json
{
  "role": "viewer",
  "is_active": false
}
```

#### `DELETE /users/{id}` — Permanently delete a user

---

### Transactions

#### `POST /transactions/` — Create transaction *(Admin)*
```json
{
  "amount": 1500.00,
  "type": "expense",
  "category": "Rent",
  "date": "2024-04-01",
  "notes": "April rent payment"
}
```

#### `GET /transactions/` — List with filters *(Analyst, Admin)*

Query parameters:
| Param       | Type   | Description                         |
|-------------|--------|-------------------------------------|
| `type`      | string | `income` or `expense`               |
| `category`  | string | Partial match, case-insensitive      |
| `date_from` | date   | Start of date range (YYYY-MM-DD)    |
| `date_to`   | date   | End of date range (YYYY-MM-DD)      |
| `page`      | int    | Page number (default: 1)            |
| `page_size` | int    | Records per page (default: 20, max: 100) |

**Response:**
```json
{
  "total": 15,
  "page": 1,
  "page_size": 20,
  "transactions": [ ... ]
}
```

#### `GET /transactions/{id}` — Single transaction *(Analyst, Admin)*

#### `PATCH /transactions/{id}` — Update transaction *(Admin)*
Send only the fields to update (partial update).

#### `DELETE /transactions/{id}` — Soft delete *(Admin)*
Sets `is_deleted=1`. The record is preserved in the database.

---

### Dashboard

#### `GET /dashboard/summary` — Full analytics summary *(Analyst, Admin)*

**Response:**
```json
{
  "total_income": 17300.00,
  "total_expenses": 5610.00,
  "net_balance": 11690.00,
  "total_transactions": 15,
  "category_totals": [
    { "category": "Salary", "total": 15000.00 },
    { "category": "Rent",   "total": 4500.00 },
    { "category": "Freelance", "total": 2000.00 }
  ],
  "monthly_trends": [
    { "month": "2024-01", "income": 6200.00, "expense": 1830.00, "net": 4370.00 },
    { "month": "2024-02", "income": 5300.00, "expense": 2020.00, "net": 3280.00 },
    { "month": "2024-03", "income": 5800.00, "expense": 1760.00, "net": 4040.00 }
  ],
  "recent_transactions": [ ... ]
}
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.10 or higher
- `pip` package manager

### Steps

```bash
# 1. Clone or extract the project
cd finance-dashboard

# 2. Create a virtual environment
python -m venv venv

# Activate it:
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Edit .env to change secret key for production
# SECRET_KEY=your_very_secret_key_here

# 5. Seed the database with sample data
python seed.py
```

The seed script will:
- Create all database tables automatically
- Create 3 users (admin, analyst, viewer)
- Insert 15 sample transactions across 3 months

---

## 🚀 Running the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- **Base URL:** `http://localhost:8000`
- **Interactive Docs (Swagger UI):** `http://localhost:8000/docs`
- **Alternative Docs (ReDoc):** `http://localhost:8000/redoc`
- **Health Check:** `http://localhost:8000/health`

---

## 🧪 Testing the API

### Using Swagger UI (Recommended)
1. Open `http://localhost:8000/docs`
2. Click **POST /auth/login** → try it out → enter credentials → execute
3. Copy the `access_token` from the response
4. Click the **Authorize 🔒** button at the top right
5. Paste the token and click Authorize
6. All subsequent requests will be authenticated

### Using curl

```bash
# Step 1: Login as admin
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@finance.com","password":"admin123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Step 2: Get dashboard summary
curl http://localhost:8000/dashboard/summary \
  -H "Authorization: Bearer $TOKEN"

# Step 3: Create a transaction
curl -X POST http://localhost:8000/transactions/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"amount": 2500, "type": "income", "category": "Bonus", "date": "2024-04-15"}'

# Step 4: Filter transactions
curl "http://localhost:8000/transactions/?type=expense&category=rent" \
  -H "Authorization: Bearer $TOKEN"
```

### Test Credentials

| Role    | Email                   | Password     |
|---------|-------------------------|--------------|
| Admin   | `admin@finance.com`     | `admin123`   |
| Analyst | `analyst@finance.com`   | `analyst123` |
| Viewer  | `viewer@finance.com`    | `viewer123`  |

---

## 📝 Assumptions & Tradeoffs

| Decision | Reasoning |
|---|---|
| **SQLite** over PostgreSQL | Simplifies local setup with zero configuration. The ORM (SQLAlchemy) makes switching to PostgreSQL a one-line change in `.env`. |
| **JWT stateless auth** | No session store needed. Tokens expire after 60 minutes (configurable in `.env`). |
| **Soft deletes for transactions** | Financial data should never be permanently erased — preserves audit trail. Users are hard-deleted since they have no audit sensitivity. |
| **Admin-only writes** | Analysts are read-only by design. If the spec required analyst writes, `require_analyst_or_above` is already defined in `dependencies.py` and can be swapped in. |
| **Amount always positive** | Transaction type (`income`/`expense`) encodes direction. Storing negative amounts would create ambiguity. |
| **No Alembic migrations** | `Base.metadata.create_all()` on startup is sufficient for this scope. A production system would use Alembic for schema evolution. |
| **CORS set to `*`** | Allows any frontend to connect during development. Should be restricted to specific origins in production. |

---

## ✨ Optional Enhancements Implemented

- ✅ **JWT Authentication** — Token-based login with expiry
- ✅ **Pagination** — All list endpoints support `page` and `page_size`
- ✅ **Soft Deletes** — Transactions are flagged, not destroyed
- ✅ **Filtering** — Transactions filterable by type, category, date range
- ✅ **Input Validation** — Pydantic v2 validators with meaningful error messages
- ✅ **Interactive API Docs** — Auto-generated Swagger UI at `/docs`
- ✅ **Seed Script** — One-command DB bootstrapping with realistic data
- ✅ **Global Error Handler** — Catches unexpected server errors gracefully
- ✅ **Audit Fields** — `created_by`, `created_at`, `updated_at` on transactions
- ✅ **Monthly Trends** — Dashboard returns per-month income/expense breakdown

---

## 🔮 What Would Come Next (Production Readiness)

- **Alembic migrations** for safe schema evolution
- **Rate limiting** (e.g. `slowapi`) to prevent abuse
- **Unit + integration tests** with `pytest` and `httpx`
- **Docker + docker-compose** for containerised deployment
- **PostgreSQL** swap (change one line in `.env`)
- **Refresh tokens** for longer-lived sessions
- **Search endpoint** across transaction notes and categories
#   f i n a n c e - d a s h b o a r d  
 