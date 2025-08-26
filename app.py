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
                st.error(res.json().get("detail", "Registration failed"))

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
    new_budget = st.number_input("Set Monthly Budget", min_value=0.0, value=st.session_state.monthly_budget)
    if st.button("Update Budget"):
        res = requests.post(
            f"{API_URL}/set_budget/{st.session_state.user_id}",
            json={"monthly_budget": new_budget}
        )
        if res.status_code == 200:
            st.session_state.monthly_budget = new_budget
            st.success(f"Budget updated to ${new_budget}")
        else:
            st.error("Failed to update budget")

    if st.button("Track Budget"):
        res = requests.get(f"{API_URL}/track_budget/{st.session_state.user_id}")
        if res.status_code == 200:
            data = res.json()
            total_spent = data["total_spent"]
            budget = data["monthly_budget"]

            # Gauge chart
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=total_spent,
                title={'text': "Spending Progress"},
                delta={'reference': budget},
                gauge={
                    'axis': {'range': [0, max(budget, total_spent*1.2)]},
                    'bar': {'color': "red"},
                    'steps': [
                        {'range': [0, budget], 'color': "lightgreen"},
                        {'range': [budget, max(budget, total_spent*1.2)], 'color': "pink"}
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
            st.error("Error tracking budget")

    # --- Expense Section ---
    st.header("🧾 Add Expense")
    date = st.date_input("Date")
    category = st.text_input("Category")
    amount = st.number_input("Amount", min_value=0.0)
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
            st.error("Failed to add expense")

    if st.button("View My Expenses"):
        res = requests.get(f"{API_URL}/view_expenses/{st.session_state.user_id}")
        if res.status_code == 200:
            expenses = res.json()
            if expenses:
                df = pd.DataFrame(expenses)

                # Drop internal DB fields
                if "id" in df: df.drop(columns=["id"], inplace=True)
                if "user_id" in df: df.drop(columns=["user_id"], inplace=True)

                # Format currency
                df["amount"] = df["amount"].map("${:,.2f}".format)

                st.subheader("📊 My Expenses")
                st.dataframe(df, use_container_width=True)

                # Totals
                total_spent = sum(
                    float(str(e["amount"]).replace("$", "").replace(",", "")) 
                    for e in expenses
                )
                st.write(f"**Total Spent:** ${total_spent:.2f}")
            else:
                st.info("No expenses recorded yet.")
        else:
            st.error("Error loading expenses")

    # --- Logout ---
    if st.button("Logout"):
        st.session_state.clear()
        st.success("Logged out!")
