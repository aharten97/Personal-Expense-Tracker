#!/usr/bin/env python3
"""
Verification script for Personal Expense Tracker Terminal
"""

import subprocess
import sys
import time
import requests
import os

def test_dependencies():
    """Test that all dependencies are available"""
    try:
        import fastapi
        import streamlit
        import uvicorn
        import pandas
        import plotly
        import sqlalchemy
        import passlib
        print("✅ All dependencies installed correctly")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def test_fastapi_server():
    """Test FastAPI server functionality"""
    print("🧪 Testing FastAPI server...")
    
    # Start server
    process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "main:app", 
        "--host", "127.0.0.1", "--port", "8000"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    time.sleep(3)
    
    try:
        # Test endpoints
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ FastAPI server working")
        else:
            print("❌ FastAPI server not responding correctly")
            return False
            
        # Test registration endpoint
        user_data = {"username": "verify_user", "password": "verify_pass"}
        reg_response = requests.post("http://127.0.0.1:8000/register", json=user_data, timeout=5)
        if reg_response.status_code == 200:
            print("✅ User registration endpoint working")
        else:
            print("⚠️ Registration test (may fail if user exists)")
            
        return True
        
    except Exception as e:
        print(f"❌ FastAPI test failed: {e}")
        return False
    finally:
        process.terminate()
        time.sleep(1)

def test_file_structure():
    """Test that all required files exist"""
    required_files = [
        "main.py",
        "streamlit_app.py", 
        "terminal_access.py",
        "requirements.txt",
        ".streamlit/config.toml",
        "README.md"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files present")
        return True

def main():
    """Run all verification tests"""
    print("🔍 Personal Expense Tracker Terminal - Verification")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Dependencies", test_dependencies),
        ("FastAPI Server", test_fastapi_server)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your terminal is ready to use.")
        print("\n🚀 To start the application, run:")
        print("   python terminal_access.py")
        print("\n🌐 Then open: http://localhost:8501")
    else:
        print("\n⚠️ Some tests failed. Please check the installation.")
        
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)