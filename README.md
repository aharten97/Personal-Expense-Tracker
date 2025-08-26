# Personal Expense Tracker 💰

Categorize & track your expenses with your monthly budget using a beautiful terminal-style web interface.

## 🚀 Quick Start - Getting Back to the Terminal

If you're asking **"How do I get back the terminal?"**, here are your options:

### Option 1: One-Click Access (Recommended)
```bash
python terminal_access.py
```

### Option 2: Manual Start
```bash
# Start the backend API
uvicorn main:app --host 0.0.0.0 --port 8000

# In another terminal, start the frontend
streamlit run streamlit_app.py
```

### Option 3: Quick URLs
- **Web Interface**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs

## 📱 Features

- 🔐 **Secure Authentication**: User registration and login
- 💰 **Budget Management**: Set and track monthly budgets
- 📊 **Expense Tracking**: Add, categorize, and manage expenses
- 📈 **Analytics**: Visual charts and spending insights
- 🎨 **Terminal Theme**: Dark terminal-style interface
- 💻 **Command-Line Feel**: Familiar terminal experience in the browser

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/aharten97/Personal-Expense-Tracker.git
   cd Personal-Expense-Tracker
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the application**:
   ```bash
   python terminal_access.py
   ```

## 🎯 Usage

1. **Access the Web Terminal**: Open http://localhost:8501 in your browser
2. **Register/Login**: Create an account or log in with existing credentials
3. **Set Budget**: Configure your monthly spending budget
4. **Add Expenses**: Track your daily expenses with categories
5. **Monitor Progress**: View analytics and budget tracking

## 🔧 API Endpoints

The FastAPI backend provides these endpoints:

- `POST /register` - Create new user account
- `POST /login` - User authentication
- `POST /set_budget/{user_id}` - Set monthly budget
- `GET /track_budget/{user_id}` - Get budget status
- `POST /add_expense` - Add new expense
- `GET /view_expenses/{user_id}` - Get user expenses
- `DELETE /delete_expense/{expense_id}` - Delete expense

## 🎨 Terminal Theme

The application uses a custom terminal theme with:
- 🟢 Green accent colors (#27AE60)
- 🌃 Dark background (#003C43)
- 🟡 Gold text (#F1C40F)
- 💻 Monospace fonts for that authentic terminal feel

## 🆘 Troubleshooting

**Can't access the terminal?**
- Make sure both servers are running
- Check that ports 8000 and 8501 are available
- Run `python terminal_access.py` to restart everything

**API connection errors?**
- Ensure the FastAPI backend is running on port 8000
- Check firewall settings if accessing remotely

**Missing dependencies?**
- Run `pip install -r requirements.txt`
- Ensure you're using Python 3.7+

## 📝 File Structure

```
Personal-Expense-Tracker/
├── main.py              # FastAPI backend application
├── app.py               # Alternative FastAPI application
├── streamlit_app.py     # Streamlit frontend (terminal interface)
├── terminal_access.py   # One-click access script
├── requirements.txt     # Python dependencies
├── Procfile            # Deployment configuration
├── .streamlit/         # Streamlit configuration
│   └── config.toml     # Terminal theme settings
└── README.md           # This file
```

## 🚀 Deployment

For production deployment on platforms like Render:

```bash
# The Procfile will automatically start the FastAPI backend
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

For local development, use the `terminal_access.py` script for the complete experience.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `python terminal_access.py`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
