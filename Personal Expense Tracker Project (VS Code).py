# main.py

from fastapi import FastAPI
from pydantic import BaseModel
import csv

app = FastAPI()

# global list to hold expenses
v_total_expenses = []

# schema for validating expenses
class Expense(BaseModel):
    date: str
    category: str
    amount: float
    description: str

# 1. ADD AN EXPENSE
@app.post("/add_expense")
def add_expense(expense: Expense):
    v_total_expenses.append(expense.dict())
    return {"message": "Expense added", "expense": expense.dict()}

# 2. VIEW LIST OF EXPENSES
@app.get("/view_expenses")
def view_expenses():
    if not v_total_expenses:
        return {"message": "No expenses recorded yet."}
    return {"expenses": v_total_expenses}

# 3. SET AND TRACK THE BUDGET
@app.get("/track_budget")
def track_budget(monthly_budget: float):
    v_total_spent = sum(i["amount"] for i in v_total_expenses)
    result = {
        "total_spent": round(v_total_spent, 2),
        "monthly_budget": monthly_budget
    }
    if v_total_spent > monthly_budget:
        result["status"] = "You have exceeded your budget!"
    else:
        result["status"] = f"You have ${round(monthly_budget - v_total_spent, 2)} left."
    return result

# 4. SAVE EXPENSES TO CSV
@app.post("/save_expenses")
def save_expenses():
    with open("expenses.csv", "w", newline="") as v_file:
        writer = csv.writer(v_file)
        writer.writerow(["date", "category", "amount", "description"])
        for i in v_total_expenses:
            writer.writerow([i["date"], i["category"], i["amount"], i["description"]])
    return {"message": "Expenses saved to file."}
