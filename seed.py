"""
Seed script — run once to create tables, an admin user, and sample transactions.

Usage:
    python seed.py
"""
import sys
from datetime import date

sys.path.insert(0, ".")  # ensure app/ is importable from project root

from app.database import Base, SessionLocal, engine
from app.models.transaction import Transaction, TransactionType
from app.models.user import User, UserRole
from app.core.security import hash_password

# ── Create tables ─────────────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# ── Seed users ────────────────────────────────────────────────────────────────
users_data = [
    {
        "full_name": "Alice Admin",
        "email": "admin@finance.com",
        "password": "admin123",
        "role": UserRole.admin,
    },
    {
        "full_name": "Bob Analyst",
        "email": "analyst@finance.com",
        "password": "analyst123",
        "role": UserRole.analyst,
    },
    {
        "full_name": "Carol Viewer",
        "email": "viewer@finance.com",
        "password": "viewer123",
        "role": UserRole.viewer,
    },
]

created_users = []
for u in users_data:
    existing = db.query(User).filter(User.email == u["email"]).first()
    if not existing:
        user = User(
            full_name=u["full_name"],
            email=u["email"],
            hashed_password=hash_password(u["password"]),
            role=u["role"],
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        created_users.append(user)
        print(f"  ✓ Created user: {user.email} (role={user.role.value})")
    else:
        created_users.append(existing)
        print(f"  → Already exists: {existing.email}")

# ── Seed transactions ─────────────────────────────────────────────────────────
admin_user = db.query(User).filter(User.email == "admin@finance.com").first()

transactions_data = [
    # Income
    {"amount": 5000.00, "type": TransactionType.income,  "category": "Salary",      "date": date(2024, 1, 5),  "notes": "January salary"},
    {"amount": 1200.00, "type": TransactionType.income,  "category": "Freelance",   "date": date(2024, 1, 18), "notes": "Web design project"},
    {"amount": 5000.00, "type": TransactionType.income,  "category": "Salary",      "date": date(2024, 2, 5),  "notes": "February salary"},
    {"amount": 300.00,  "type": TransactionType.income,  "category": "Investments", "date": date(2024, 2, 20), "notes": "Dividend payout"},
    {"amount": 5000.00, "type": TransactionType.income,  "category": "Salary",      "date": date(2024, 3, 5),  "notes": "March salary"},
    {"amount": 800.00,  "type": TransactionType.income,  "category": "Freelance",   "date": date(2024, 3, 22), "notes": "Logo design"},
    # Expenses
    {"amount": 1500.00, "type": TransactionType.expense, "category": "Rent",        "date": date(2024, 1, 1),  "notes": "January rent"},
    {"amount": 250.00,  "type": TransactionType.expense, "category": "Groceries",   "date": date(2024, 1, 10), "notes": "Weekly groceries"},
    {"amount": 80.00,   "type": TransactionType.expense, "category": "Utilities",   "date": date(2024, 1, 15), "notes": "Electricity bill"},
    {"amount": 1500.00, "type": TransactionType.expense, "category": "Rent",        "date": date(2024, 2, 1),  "notes": "February rent"},
    {"amount": 120.00,  "type": TransactionType.expense, "category": "Transport",   "date": date(2024, 2, 14), "notes": "Monthly metro pass"},
    {"amount": 400.00,  "type": TransactionType.expense, "category": "Dining",      "date": date(2024, 2, 28), "notes": "Team dinner"},
    {"amount": 1500.00, "type": TransactionType.expense, "category": "Rent",        "date": date(2024, 3, 1),  "notes": "March rent"},
    {"amount": 60.00,   "type": TransactionType.expense, "category": "Utilities",   "date": date(2024, 3, 12), "notes": "Internet bill"},
    {"amount": 200.00,  "type": TransactionType.expense, "category": "Groceries",   "date": date(2024, 3, 20), "notes": "Monthly grocery run"},
]

existing_count = db.query(Transaction).count()
if existing_count == 0:
    for t in transactions_data:
        tx = Transaction(**t, created_by=admin_user.id)
        db.add(tx)
    db.commit()
    print(f"\n  ✓ Seeded {len(transactions_data)} transactions")
else:
    print(f"\n  → Transactions already exist ({existing_count} records), skipping")

db.close()

print("\n✅ Seed complete! You can now start the server with:")
print("   uvicorn app.main:app --reload")
print("\n📋 Test credentials:")
print("   admin@finance.com   / admin123")
print("   analyst@finance.com / analyst123")
print("   viewer@finance.com  / viewer123")
