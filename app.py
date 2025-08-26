import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

# Use your deployed backend URL from Render
API_URL = "https://personal-expense-tracker-1-vub6.onrender.com"

st.set_page_config(page_title="Personal Expense Tracker", page_icon="💰", layout="centered")
st.title("💰 Personal Expense Tracker")

# ---------------------------
# Login / Register
# ---------------------------
if "user_id" not in st.session_state:
    st.subheader("Login or Register")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Register"):
            res = requests.post(f"{API_URL}/register", json={"username": username, "password": password})
            if res.status_code == 200:
                st.success("User registered! Now log in.")
            else:
                try:
                    st.error(res.json().get("detail", "Registration failed"))
                except:
                    st.error(f"Registration failed: {res.text}")

    with col2:
        if st.button("Login"):
            res = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
            if res.status_code == 200 and "user_id" in res.json():
                st.session_state.user_id = res.json()["user_id"]
                st.session_state.username = username
                st.session_state.monthly_budget = res.json().get("monthly_budget", 0.0)
                st.success(f"Welcome back, {username}!")
            else:
                st.error("Invalid login")

# ---------------------------
# If logged in → Show Tracker
# ---------------------------
else:
    st.success(f"Logged in as {st.session_state.username}")

    # --- Budget Section ---
    st.header("💵 Monthly Budget")

    # Use text input so typing works smoothly
    budget_input = st.text_input("Set Monthly Budget", value=f"{st.session_state.monthly_budget:.2f}")
    try:
        new_budget = round(float(budget_input), 2) if budget_input else 0.0
    except ValueError:
        new_budget = 0.0
        st.warning("Please enter a valid number for the budget.")

    if st.button("Update Budget"):
        res = requests.post(
            f"{API_URL}/set_budget/{st.session_state.user_id}",
            json={"monthly_budget": new_budget}
        )
        if res.status_code == 200:
            st.session_state.monthly_budget = new_budget
            st.success(f"Budget updated to ${new_budget:.2f}")
        else:
            try:
                st.error(res.json().get("detail", f"Failed to update budget: {res.text}"))
            except:
                st.error(f"Failed to update budget: {res.text}")

    if st.button("Track Budget"):
        res = requests.get(f"{API_URL}/track_budget/{st.session_state.user_id}")
        if res.status_code == 200:
            data = res.json()

            total_spent = round(data["total_spent"], 2)
            budget = round(data["monthly_budget"], 2)

            # Gauge chart with $ labels
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=total_spent,
                title={'text': "Spending Progress"},
                number={'prefix': "$", 'valueformat': ".2f"},
                delta={'reference': budget, 'relative': False, 'valueformat': ".2f", 'prefix': "$"},
                gauge={
                    'axis': {'range': [0, max(budget, total_spent * 1.2)]},
                    'bar': {'color': "red"},
                    'steps': [
                        {'range': [0, budget], 'color': "lightgreen"},
                        {'range': [budget, max(budget, total_spent * 1.2)], 'color': "pink"}
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 4},
                        'thickness': 0.75,
                        'value': budget
                    }
                }
            ))

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error(f"Error tracking budget: {res.text}")

    # --- Expense Section ---
    st.header("🧾 Add Expense")
    date = st.date_input("Date")
    category = st.text_input("Category")

    # Fix typing issue for expense amount
    amount_input = st.text_input("Amount", value="0.00")
    try:
        amount = round(float(amount_input), 2) if amount_input else 0.0
    except ValueError:
        amount = 0.0
        st.warning("Please enter a valid number for the expense amount.")

    description = st.text_area("Description")

    if st.button("Add Expense"):
        payload = {
            "user_id": st.session_state.user_id,
            "date": str(date),
            "category": category,
            "amount": amount,
            "description": description
        }
        res = requests.post(f"{API_URL}/add_expense", json=payload)
        if res.status_code == 200:
            st.success("Expense added!")
        else:
            st.error(f"Failed to add expense: {res.text}")

    if st.button("View My Expenses"):
        res = requests.get(f"{API_URL}/view_expenses/{st.session_state.user_id}")
        if res.status_code == 200:
            expenses = res.json()
            if expenses:
                df = pd.DataFrame(expenses)

                # Drop DB internal fields
                if "id" in df: df.drop(columns=["id"], inplace=True)
                if "user_id" in df: df.drop(columns=["user_id"], inplace=True)

                # ✅ Calculate total before formatting
                total_spent = round(df["amount"].astype(float).sum(), 2)

                # Format amount column AFTER total is calculated
                df["amount"] = df["amount"].map(lambda x: f"${float(x):,.2f}")

                st.subheader("📊 My Expenses")
                st.dataframe(df, use_container_width=True)

                st.write(f"**Total Spent:** ${total_spent:.2f}")
            else:
                st.info("No expenses recorded yet.")
        else:
            st.error(f"Error loading expenses: {res.text}")

    # --- Logout ---
    if st.button("Logout"):
        st.session_state.clear()
        st.success("Logged out!")
