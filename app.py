import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

# Backend URL on Render
API_URL = "https://personal-expense-tracker-1-vub6.onrender.com"

st.set_page_config(page_title="Personal Expense Tracker", page_icon="💰", layout="centered")
st.title("💰 Personal Expense Tracker")

# ---------------------------
# Login / Register
# ---------------------------
if "user_id" not in st.session_state:
    st.subheader("Existing User Login or New User Register")

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
            spent = round(data["total_spent"], 2)
            budget = round(data["monthly_budget"], 2)
            remaining = round(budget - spent, 2)

            # ✅ Gauge chart: Remaining big in white, Spent small in red
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=remaining,
                title={'text': "Spending Progress"},
                number={'prefix': "$", 'valueformat': ".2f",
                        'font': {'size': 40, 'color': "white"}},

                delta={
                    'reference': budget,
                    'relative': False,
                    'valueformat': ".2f",
                    'prefix': "Spent: $ ",
                    'increasing': {'color': "red"}
                },

                gauge={
                    'axis': {'range': [0, max(budget, spent * 1.2)]},
                    'bar': {'color': "white"},
                    'steps': [
                        {'range': [0, remaining], 'color': "lightgreen"},
                        {'range': [remaining, budget], 'color': "red"}
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
            st.rerun()
        else:
            st.error(f"Failed to add expense: {res.text}")

    # ✅ Always show the expense list
    res = requests.get(f"{API_URL}/view_expenses/{st.session_state.user_id}")
    if res.status_code == 200:
        expenses = res.json()
        if expenses:
            df = pd.DataFrame(expenses)

            if "user_id" in df:
                df.drop(columns=["user_id"], inplace=True)

            if "id" not in df:
                st.warning("Expenses missing ID field, cannot delete rows.")
            else:
                st.subheader("📊 My Expenses")

                # ✅ Wider columns so DELETE header doesn't wrap
                header_cols = st.columns([1, 2, 3, 2, 2, 3])
                headers = ["ID", "CATEGORY", "DESCRIPTION", "DATE", "AMOUNT", "DELETE"]
                for col, header in zip(header_cols, headers):
                    col.markdown(f"**{header}**")

                delete_triggered = None

                # ✅ Display rows with delete buttons
                for _, row in df.iterrows():
                    expense_id = int(row["id"])
                    cols = st.columns([1, 2, 3, 2, 2, 3])
                    cols[0].write(expense_id)
                    cols[1].write(row["category"])
                    cols[2].write(row["description"])
                    cols[3].write(row["date"])
                    cols[4].write(f"${float(row['amount']):,.2f}")

                    if cols[5].button("🗑️", key=f"del_{expense_id}"):
                        delete_triggered = expense_id

                # ✅ Process deletion outside the loop
                if delete_triggered is not None:
                    try:
                        del_res = requests.delete(f"{API_URL}/delete_expense/{delete_triggered}")
                        if del_res.status_code == 200:
                            st.success(f"Deleted expense ID {delete_triggered}")
                            st.rerun()  # refresh list automatically
                        else:
                            st.error(f"Failed to delete: {del_res.text}")
                    except Exception as e:
                        st.error(f"Error deleting: {e}")

                # ✅ Total Spent
                total_spent = round(df["amount"].astype(float).sum(), 2)
                st.write(f"**Total Spent:** ${total_spent:.2f}")
        else:
            st.info("No expenses recorded yet.")
    else:
        st.error(f"Error loading expenses: {res.text}")

    # --- Logout ---
    if st.button("Logout"):
        st.session_state.clear()
        st.success("Logged out!")