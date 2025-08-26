import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import date, datetime
import json

# Configure the page
st.set_page_config(
    page_title="Personal Expense Tracker Terminal",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Base URL
API_BASE = "http://localhost:8000"

def init_session_state():
    """Initialize session state variables"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'monthly_budget' not in st.session_state:
        st.session_state.monthly_budget = 0.0

def api_request(endpoint, method="GET", data=None):
    """Make API request to FastAPI backend"""
    url = f"{API_BASE}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        
        if response.status_code == 200:
            return response.json(), True
        else:
            return response.json(), False
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to the expense tracker API. Make sure the FastAPI server is running.")
        st.info("Run: `uvicorn main:app --host 0.0.0.0 --port 8000` in your terminal")
        return None, False
    except Exception as e:
        st.error(f"❌ API Error: {str(e)}")
        return None, False

def terminal_style_container():
    """Apply terminal-like styling"""
    st.markdown("""
    <style>
    .main-container {
        background-color: #003C43;
        color: #F1C40F;
        font-family: 'Courier New', monospace;
    }
    .terminal-header {
        background: linear-gradient(90deg, #27AE60, #003C43);
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .command-line {
        background-color: #1C1F26;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #27AE60;
        margin: 10px 0;
    }
    .success-msg {
        color: #27AE60;
        font-weight: bold;
    }
    .error-msg {
        color: #E74C3C;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

def show_terminal_header():
    """Display terminal-style header"""
    st.markdown("""
    <div class="terminal-header">
        <h1>💰 Personal Expense Tracker Terminal</h1>
        <p>A command-line style interface for managing your expenses</p>
    </div>
    """, unsafe_allow_html=True)

def login_interface():
    """Login/Register interface"""
    st.markdown("## 🔐 Authentication Terminal")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.markdown("### Login to Access Your Expenses")
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            login_btn = st.form_submit_button("🚀 Login", use_container_width=True)
            
            if login_btn:
                if username and password:
                    data = {"username": username, "password": password}
                    result, success = api_request("/login", "POST", data)
                    
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.user_id = result["user_id"]
                        st.session_state.username = username
                        st.session_state.monthly_budget = result["monthly_budget"]
                        st.success("✅ Login successful! Welcome to your expense terminal.")
                        st.rerun()
                    else:
                        st.error("❌ Login failed. Please check your credentials.")
                else:
                    st.warning("⚠️ Please enter both username and password.")
    
    with tab2:
        st.markdown("### Create New Account")
        with st.form("register_form"):
            new_username = st.text_input("New Username", placeholder="Choose a username")
            new_password = st.text_input("New Password", type="password", placeholder="Choose a password")
            register_btn = st.form_submit_button("📝 Register", use_container_width=True)
            
            if register_btn:
                if new_username and new_password:
                    data = {"username": new_username, "password": new_password}
                    result, success = api_request("/register", "POST", data)
                    
                    if success:
                        st.success("✅ Registration successful! You can now login.")
                    else:
                        st.error("❌ Registration failed. Username may already exist.")
                else:
                    st.warning("⚠️ Please enter both username and password.")

def expense_dashboard():
    """Main expense tracking dashboard"""
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"### 💻 Welcome, {st.session_state.username}!")
    
    with col2:
        if st.button("💰 Set Budget"):
            st.session_state.show_budget_modal = True
    
    with col3:
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.username = None
            st.rerun()

def budget_management():
    """Budget management section"""
    st.markdown("## 💰 Budget Terminal")
    
    # Get current budget status
    result, success = api_request(f"/track_budget/{st.session_state.user_id}")
    
    if success:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Monthly Budget", f"${result['monthly_budget']:.2f}")
        
        with col2:
            st.metric("Total Spent", f"${result['total_spent']:.2f}")
        
        with col3:
            remaining = result['remaining']
            st.metric("Remaining", f"${remaining:.2f}", 
                     delta=None if remaining >= 0 else "Over Budget!")
        
        with col4:
            status_color = "🟢" if result['status'] == "Within budget" else "🔴"
            st.metric("Status", f"{status_color} {result['status']}")
    
    # Set new budget
    with st.expander("🔧 Update Monthly Budget"):
        with st.form("budget_form"):
            new_budget = st.number_input("New Monthly Budget ($)", min_value=0.0, value=float(st.session_state.monthly_budget), step=50.0)
            if st.form_submit_button("💾 Update Budget"):
                data = {"monthly_budget": new_budget}
                result, success = api_request(f"/set_budget/{st.session_state.user_id}", "POST", data)
                
                if success:
                    st.session_state.monthly_budget = new_budget
                    st.success("✅ Budget updated successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to update budget.")

def expense_management():
    """Expense management section"""
    st.markdown("## 📊 Expense Management Terminal")
    
    tab1, tab2, tab3 = st.tabs(["➕ Add Expense", "📋 View Expenses", "📈 Analytics"])
    
    with tab1:
        st.markdown("### Add New Expense")
        with st.form("expense_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                expense_date = st.date_input("Date", value=date.today())
                category = st.selectbox("Category", 
                    ["Food", "Transportation", "Housing", "Entertainment", "Healthcare", "Shopping", "Utilities", "Other"])
            
            with col2:
                amount = st.number_input("Amount ($)", min_value=0.01, step=0.01)
                description = st.text_area("Description", placeholder="Optional description...")
            
            if st.form_submit_button("💾 Add Expense", use_container_width=True):
                data = {
                    "user_id": st.session_state.user_id,
                    "date": expense_date.isoformat(),
                    "category": category,
                    "amount": amount,
                    "description": description
                }
                
                result, success = api_request("/add_expense", "POST", data)
                
                if success:
                    st.success("✅ Expense added successfully!")
                    st.balloons()
                else:
                    st.error("❌ Failed to add expense.")
    
    with tab2:
        st.markdown("### Your Expense History")
        
        # Get expenses
        result, success = api_request(f"/view_expenses/{st.session_state.user_id}")
        
        if success and result:
            # Convert to DataFrame
            df = pd.DataFrame(result)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date', ascending=False)
            
            # Display summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Expenses", len(df))
            with col2:
                st.metric("Total Amount", f"${df['amount'].sum():.2f}")
            with col3:
                st.metric("Average Expense", f"${df['amount'].mean():.2f}")
            
            # Display expenses table
            st.markdown("#### Recent Expenses")
            for _, expense in df.head(10).iterrows():
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 3, 1])
                    
                    with col1:
                        st.write(f"📅 {expense['date'].strftime('%Y-%m-%d')}")
                    with col2:
                        st.write(f"🏷️ {expense['category']}")
                    with col3:
                        st.write(f"💵 ${expense['amount']:.2f}")
                    with col4:
                        st.write(f"📝 {expense['description'][:50]}...")
                    with col5:
                        if st.button("🗑️", key=f"delete_{expense['id']}"):
                            delete_result, delete_success = api_request(f"/delete_expense/{expense['id']}", "DELETE")
                            if delete_success:
                                st.success("✅ Expense deleted!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to delete expense.")
                    
                    st.divider()
        else:
            st.info("📋 No expenses found. Add your first expense to get started!")
    
    with tab3:
        st.markdown("### Expense Analytics")
        
        # Get expenses for analytics
        result, success = api_request(f"/view_expenses/{st.session_state.user_id}")
        
        if success and result:
            df = pd.DataFrame(result)
            df['date'] = pd.to_datetime(df['date'])
            
            # Category breakdown
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Expenses by Category")
                category_total = df.groupby('category')['amount'].sum().reset_index()
                fig_pie = px.pie(category_total, values='amount', names='category', 
                               title="Spending by Category",
                               color_discrete_sequence=px.colors.qualitative.Set3)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                st.markdown("#### Monthly Spending Trend")
                df['month'] = df['date'].dt.to_period('M').astype(str)
                monthly_total = df.groupby('month')['amount'].sum().reset_index()
                fig_line = px.line(monthly_total, x='month', y='amount', 
                                 title="Monthly Spending Trend",
                                 markers=True)
                st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("📊 No data available for analytics.")

def main():
    """Main application"""
    init_session_state()
    terminal_style_container()
    show_terminal_header()
    
    if not st.session_state.logged_in:
        login_interface()
    else:
        # Main dashboard
        expense_dashboard()
        
        # Navigation sidebar
        with st.sidebar:
            st.markdown("## 🎛️ Command Panel")
            
            page = st.radio("Navigate to:", [
                "💰 Budget Management",
                "📊 Expense Management", 
                "ℹ️ About"
            ])
            
            st.markdown("---")
            st.markdown("### 💡 Quick Commands")
            st.markdown("""
            - **Ctrl + R**: Refresh data
            - **Tab**: Navigate between sections
            - **Enter**: Submit forms
            """)
        
        # Show selected page
        if page == "💰 Budget Management":
            budget_management()
        elif page == "📊 Expense Management":
            expense_management()
        elif page == "ℹ️ About":
            st.markdown("## ℹ️ About This Terminal")
            st.markdown("""
            This is a **terminal-style interface** for managing your personal expenses. 
            
            ### Features:
            - 🔐 Secure user authentication
            - 💰 Monthly budget tracking
            - 📊 Expense categorization
            - 📈 Visual analytics
            - 🎨 Terminal-themed UI
            
            ### Getting Started:
            1. Set your monthly budget
            2. Add your daily expenses
            3. Track your spending habits
            4. Stay within budget!
            
            ### Need Help?
            If you lost access to this terminal, you can always return by:
            1. Starting the FastAPI server: `uvicorn main:app --host 0.0.0.0 --port 8000`
            2. Starting this Streamlit app: `streamlit run streamlit_app.py`
            3. Opening your browser to the Streamlit URL
            """)

if __name__ == "__main__":
    main()