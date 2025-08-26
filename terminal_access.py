#!/usr/bin/env python3
"""
Personal Expense Tracker Terminal Access Script
===============================================

This script helps you get back to the terminal and access your expense tracker.
"""

import subprocess
import sys
import os
import signal
import time
import requests

def print_banner():
    """Print welcome banner"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                Personal Expense Tracker Terminal            ║
║                                                              ║
║  💰 Your personal finance management system                  ║
║  🎯 Track expenses, manage budgets, analyze spending         ║
╚══════════════════════════════════════════════════════════════╝
    """)

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import streamlit
        import uvicorn
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("📦 Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True

def is_port_in_use(port):
    """Check if a port is in use"""
    try:
        response = requests.get(f"http://localhost:{port}", timeout=1)
        return True
    except:
        return False

def start_backend():
    """Start the FastAPI backend"""
    if is_port_in_use(8000):
        print("✅ FastAPI backend already running on port 8000")
        return None
    
    print("🚀 Starting FastAPI backend server...")
    process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "main:app", 
        "--host", "0.0.0.0", "--port", "8000"
    ])
    
    # Wait for server to start
    for i in range(10):
        if is_port_in_use(8000):
            print("✅ FastAPI backend started successfully!")
            return process
        time.sleep(1)
        print(f"⏳ Waiting for backend to start... ({i+1}/10)")
    
    print("❌ Failed to start FastAPI backend")
    return None

def start_frontend():
    """Start the Streamlit frontend"""
    if is_port_in_use(8501):
        print("✅ Streamlit frontend already running on port 8501")
        return None
    
    print("🎨 Starting Streamlit frontend...")
    process = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
        "--server.port", "8501", "--server.address", "0.0.0.0",
        "--server.headless", "true"
    ])
    
    # Wait for server to start
    for i in range(15):
        if is_port_in_use(8501):
            print("✅ Streamlit frontend started successfully!")
            return process
        time.sleep(1)
        print(f"⏳ Waiting for frontend to start... ({i+1}/15)")
    
    print("❌ Failed to start Streamlit frontend")
    return None

def show_access_info():
    """Show how to access the application"""
    print("""
🎯 ACCESS YOUR EXPENSE TRACKER:

📱 Web Interface (Recommended):
   Open your browser and go to: http://localhost:8501
   
🔧 API Documentation:
   FastAPI Swagger UI: http://localhost:8000/docs
   
📋 Quick Commands:
   • Register a new account or login
   • Set your monthly budget
   • Add daily expenses
   • View spending analytics
   • Track budget progress

🆘 HOW TO GET BACK TO THE TERMINAL:

   1. CTRL+C in this window to stop servers
   2. Or run: python terminal_access.py
   3. Or manually start:
      - Backend: uvicorn main:app --host 0.0.0.0 --port 8000
      - Frontend: streamlit run streamlit_app.py

💡 TIP: Bookmark http://localhost:8501 for easy access!
    """)

def cleanup_handler(signum, frame):
    """Handle cleanup on exit"""
    print("\n🛑 Shutting down servers...")
    # Kill any remaining processes
    try:
        subprocess.run(["pkill", "-f", "uvicorn"], check=False)
        subprocess.run(["pkill", "-f", "streamlit"], check=False)
    except:
        pass
    print("✅ Cleanup complete. You're back to the terminal!")
    sys.exit(0)

def main():
    """Main function"""
    print_banner()
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, cleanup_handler)
    
    # Check if we're in the right directory
    if not os.path.exists("main.py") or not os.path.exists("streamlit_app.py"):
        print("❌ Error: Please run this script from the Personal-Expense-Tracker directory")
        print("📁 Current directory:", os.getcwd())
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Start servers
    backend_process = start_backend()
    time.sleep(2)  # Give backend time to start
    frontend_process = start_frontend()
    
    # Show access information
    show_access_info()
    
    # Keep script running
    try:
        print("🔄 Servers are running... Press CTRL+C to stop and return to terminal")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup_handler(None, None)

if __name__ == "__main__":
    main()