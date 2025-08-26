import streamlit as st
import requests

# Replace this with your Codespaces URL for FastAPI (port 8000)
API_URL = "https://urban-space-xxxx-8000.app.github.dev"

st.title("💰 Personal Expense Tracker")

# Input fields
date = st.date_input("Date")
category = st.text_input("Category")
amount = st.number_input("Amount", min_value=0.0)
description = st.text_area("Description")

# Button to add expense
if st.button("Add Expense"):
    payload = {
        "date": str(date),
        "category": category,
        "amount": amount,
        "description": description
    }
    res = requests.post(f"{API_URL}/add_expense", json=payload)
    if res.status_code == 200:
        st.success(res.json()["message"])
    else:
        st.error("Failed to add expense")

# Button to view expenses
if st.button("View Expenses"):
    res = requests.get(f"{API_URL}/view_expenses").json()
    if "expenses" in res:
        st.table(res["expenses"])
    else:
        st.write(res["message"])

# Track budget
budget = st.number_input("Monthly Budget", min_value=0.0)
if st.button("Track Budget"):
    res = requests.get(f"{API_URL}/track_budget", params={"monthly_budget": budget}).json()
    st.json(res)

# Save expenses
if st.button("Save Expenses"):
    res = requests.post(f"{API_URL}/save_expenses").json()
    st.success(res["message"])