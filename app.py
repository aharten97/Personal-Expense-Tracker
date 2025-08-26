from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
import os

# Database setup (Render provides DATABASE_URL, fallback is SQLite for local testing)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------------------------
# Database Models
# ---------------------------
class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    monthly_budget = Column(Float, default=0.0)

class ExpenseDB(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    date = Column(String)
    category = Column(String)
    amount = Column(Float)
    description = Column(String)

Base.metadata.create_all(bind=engine)

# ---------------------------
# Pydantic Schemas
# ---------------------------
class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class BudgetUpdate(BaseModel):
    monthly_budget: float

class Expense(BaseModel):
    user_id: int
    date: str
    category: str
    amount: float
    description: str

# ---------------------------
# Dependency
# ---------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------
# Authentication Endpoints
# ---------------------------
@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(UserDB).filter(UserDB.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    hashed_pw = pwd_context.hash(user.password)
    db_user = UserDB(username=user.username, hashed_password=hashed_pw)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User registered successfully", "user_id": db_user.id}

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(UserDB).filter(UserDB.username == user.username).first()
    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {
        "message": "Login successful",
        "user_id": db_user.id,
        "monthly_budget": db_user.monthly_budget
    }

# ---------------------------
# Budget Management
# ---------------------------
@app.post("/set_budget/{user_id}")
def set_budget(user_id: int, budget: BudgetUpdate, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.monthly_budget = budget.monthly_budget
    db.commit()
    return {"message": "Budget updated", "monthly_budget": user.monthly_budget}

@app.get("/track_budget/{user_id}")
def track_budget(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    total_spent = sum(e.amount for e in db.query(ExpenseDB).filter(ExpenseDB.user_id == user_id).all())
    remaining = user.monthly_budget - total_spent
    return {
        "total_spent": round(total_spent, 2),
        "monthly_budget": user.monthly_budget,
        "remaining": round(remaining, 2),
        "status": "Over budget!" if remaining < 0 else "Within budget"
    }

# ---------------------------
# Expense Management
# ---------------------------
@app.post("/add_expense")
def add_expense(expense: Expense, db: Session = Depends(get_db)):
    db_expense = ExpenseDB(**expense.dict())
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return {"message": "Expense added", "expense_id": db_expense.id}

@app.get("/view_expenses/{user_id}")
def view_expenses(user_id: int, db: Session = Depends(get_db)):
    return db.query(ExpenseDB).filter(ExpenseDB.user_id == user_id).all()

@app.delete("/delete_expense/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.query(ExpenseDB).filter(ExpenseDB.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(expense)
    db.commit()
    return {"message": f"Expense with ID {expense_id} deleted successfully"}

# ---------------------------
# Home
# ---------------------------
@app.get("/")
def home():
    return {"message": "Welcome to the Personal Expense Tracker API with Users and Budgets. Visit /docs for the interactive UI."}
