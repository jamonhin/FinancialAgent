# Development Commands for Financial Agent

> **⚠️ ENVIRONMENT UPDATE:** The previous `financial_agent_env` was corrupted and has been replaced with a new `venv` environment. All commands below have been updated to use `venv`.

## 🚀 QUICK REFERENCE

### Stop the App
```bash
pkill -f "python app.py"
```

### Start the App
```bash
# 1. Activate environment
source venv/bin/activate

# 2. Start app in background
nohup python app.py > app.log 2>&1 &
```

### Check App Status
```bash
# Check if running
lsof -i :8050

# Check logs
tail -f app.log
```

---

## 🏗️ INITIAL ENVIRONMENT SETUP (Run once)

### Automated Setup (Recommended)
```bash
# Navigate to project directory
cd /Users/jamesmontoya/Documents/github/FinancialAgent

# Run the setup script (creates virtual environment and installs dependencies)
chmod +x setup.sh
./setup.sh

# Follow the prompts to configure your .env file with API keys
```

### Manual Setup (Alternative)
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (if needed)
cp .env.example .env
# Edit .env file and add your API keys
```

## 🔍 ENVIRONMENT VERIFICATION (Always check first!)

### Complete Environment Verification Steps
```bash
# Step 1: Check your terminal prompt for environment indicators
echo "Current prompt shows: $PS1"

# Step 2: Verify Python path and version
which python
python --version
python -c "import sys; print('Python path:', sys.executable)"

# Step 3: Check if virtual environment is properly activated
echo "Virtual environment: $VIRTUAL_ENV"

# Step 4: Verify port is free before starting
lsof -i :8050

# Look for these patterns:
# ✅ CLEAN: "jamesmontoya@Jamess-MacBook-Pro FinancialAgent %"
# ⚠️  ACTIVE: "(venv) jamesmontoya@Jamess-MacBook-Pro FinancialAgent %"
```

### Expected Results When Environment is Active
```bash
# Prompt should show:
(venv) jamesmontoya@Jamess-MacBook-Pro FinancialAgent %

# Python path should be:
/Users/jamesmontoya/Documents/github/FinancialAgent/venv/bin/python

# Python version should be:
Python 3.13.3

# Virtual environment should show:
/Users/jamesmontoya/Documents/github/FinancialAgent/venv

# Port check should return:
(empty - meaning port 8050 is free)
```

### Check Current Environment Status
```bash
# Quick environment status check
echo "=== ENVIRONMENT STATUS ==="
echo "Prompt: $(echo $PS1)"
echo "Python: $(which python)"
echo "Version: $(python --version)"
echo "VirtEnv: $(echo $VIRTUAL_ENV)"
echo "Port 8050: $(lsof -i :8050 | wc -l) processes"
echo "========================="
```s for Financial Agent

## � ENVIRONMENT VERIFICATION (Always check first!)

### Check Current Environment Status
```bash
# Check your terminal prompt for environment indicators
echo "Current prompt shows: $PS1"

# Look for these patterns:
# ✅ CLEAN: "jamesmontoya@Jamess-MacBook-Pro FinancialAgent %"
# ⚠️  ACTIVE: "(financial_agent_env) jamesmontoya@Jamess-MacBook-Pro FinancialAgent %"

# Check which Python you're using
which python
which pip

# Check Python version and path
python --version
python -c "import sys; print('Python path:', sys.executable)"
```

### Environment States
```bash
# 🟢 DEACTIVATED (Clean state):
# Prompt: jamesmontoya@Jamess-MacBook-Pro FinancialAgent %
# Python: /usr/bin/python3 or /opt/homebrew/bin/python3

# 🟡 ACTIVATED (Virtual environment):
# Prompt: (venv) jamesmontoya@Jamess-MacBook-Pro FinancialAgent %
# Python: /Users/jamesmontoya/Documents/github/FinancialAgent/venv/bin/python
```

## � HOW TO STOP THE APP (Quick Reference)

### Simple Stop Command
```bash
# Method 1: Kill by process name (most reliable)
pkill -f "python app.py"

# Method 2: Kill by port (if method 1 doesn't work)
lsof -i :8050
kill -9 [PID_NUMBER]

# Method 3: Nuclear option (kills all Python processes)
pkill -9 python
```

### Verify App is Stopped
```bash
lsof -i :8050
# Should return nothing if stopped successfully
```

## �🔄 ENVIRONMENT MANAGEMENT

### Activate Virtual Environment
```bash
# Navigate to project directory
cd /Users/jamesmontoya/Documents/github/FinancialAgent

# Activate virtual environment
source venv/bin/activate

# ✅ Verify activation (should see prefix in prompt)
# Expected: (venv) jamesmontoya@Jamess-MacBook-Pro FinancialAgent %
```

### Deactivate Virtual Environment
```bash
# Deactivate environment
deactivate

# ✅ Verify deactivation (prefix should be gone)
# Expected: jamesmontoya@Jamess-MacBook-Pro FinancialAgent %
```

## �🛑 STOP APP (Always do this FIRST before making changes)
```bash
# Method 1: Kill by process name
pkill -f "python app.py"

# Method 2: Kill by port (if method 1 doesn't work)
lsof -i :8050
kill -9 [PID_NUMBER]

# Method 3: Nuclear option
pkill -9 python
```

## ✅ VERIFY APP IS STOPPED
```bash
lsof -i :8050
# Should return nothing if stopped successfully
```

## 🚀 START APP (Only after making changes and activating environment)
```bash
# 1. FIRST: Activate environment
source venv/bin/activate

# 2. Verify environment is active (check prompt)
# Should show: (venv) jamesmontoya@Jamess-MacBook-Pro FinancialAgent %

# 3. Test imports
python -c "from app import app; print('✅ App imports OK')"

# 4. Start app
# Background mode (recommended for development)
nohup python app.py > app.log 2>&1 &

# OR Foreground mode (to see live logs)
python app.py
```

## 📋 CHECK APP STATUS
```bash
# Check if running
lsof -i :8050

# Check logs
tail -f app.log

# Check environment while app is running
echo "Environment active: $(echo $VIRTUAL_ENV)"
```

## ⚠️ TROUBLESHOOTING

## ⚠️ TROUBLESHOOTING

### Virtual Environment & Threading Debug Features

The app includes debugging features for virtual environment and Dash hot reloader issues:

#### Environment Variables for Debugging
```bash
# Enable thread debugging (shows thread IDs and lifecycle)
export DEBUG_THREADING=true

# Disable background threads (runs analysis synchronously)  
export DISABLE_BACKGROUND_THREADS=true

# Use simulated results (faster UI testing)
export SIMULATE_ANALYSIS_RESULTS=true

# Start app with debugging enabled
nohup python app.py > app.log 2>&1 &

# Check debug output
tail -f app.log
```

#### Thread Debugging Steps
```bash
# 1. Enable thread debugging and start app
export DEBUG_THREADING=true
source venv/bin/activate
python app.py

# 2. Watch for thread information in logs
# Look for messages like:
# [DEBUG] Thread 123456 (ThreadPoolExecutor-0_0): BACKGROUND ANALYSIS STARTED
# [DEBUG] Thread 123456 (ThreadPoolExecutor-0_0): Active threads after analysis: 3

# 3. Check for lingering threads after hot reload
# Each analysis should show thread start/end with IDs
```

#### UI Testing Without Background Threads
```bash
# Disable threads and use simulated results for smooth UI development
export DISABLE_BACKGROUND_THREADS=true
export SIMULATE_ANALYSIS_RESULTS=true
source venv/bin/activate
python app.py

# UI changes will reload faster without background thread complications
```

#### Debug Script Usage
```bash
# Run comprehensive threading test
python debug_threading.py

# Set up debug environment variables
python debug_threading.py setup

# Monitor threads for 60 seconds
python debug_threading.py monitor 60

# Check app status only
python debug_threading.py status
```

#### Manual Thread Control (Code-level Debugging)
```python
# In app.py, line ~945, you can comment out analysis_thread.start():
# analysis_thread.start()  # Comment this line to prevent thread execution

# This allows testing UI without any background processing
```

### If Terminal Prompt Looks Wrong:
```bash
# If you see corrupted prompt or strange paths:
deactivate  # Deactivate first
cd /Users/jamesmontoya/Documents/github/FinancialAgent  # Navigate to project
source venv/bin/activate  # Reactivate cleanly
```

### If App Won't Start:
```bash
# 1. Check environment
which python  # Should show virtual env path when activated

# 2. Check dependencies
pip list | grep -E "(dash|plotly|crewai|yfinance)"

# 3. Reinstall if needed
pip install -r requirements.txt
```

## 📋 COMPLETE STARTUP WORKFLOW

### 🚀 Safe App Startup Process (Follow in Order)
```bash
# 1. Navigate to project directory
cd /Users/jamesmontoya/Documents/github/FinancialAgent

# 2. Activate virtual environment
source venv/bin/activate

# 3. Verify environment activation (CRITICAL!)
# Check prompt - should show: (venv) jamesmontoya@Jamess-MacBook-Pro FinancialAgent %
which python
# Should return: /Users/jamesmontoya/Documents/github/FinancialAgent/venv/bin/python

python --version
# Should return: Python 3.13.3

echo "Virtual environment: $VIRTUAL_ENV"
# Should return: /Users/jamesmontoya/Documents/github/FinancialAgent/venv

# 4. Ensure no app is running
lsof -i :8050
# Should return empty (no processes on port 8050)

# 5. Test app imports
python -c "from app import app; print('✅ App imports successfully')"

# 6. Start the app
nohup python app.py > app.log 2>&1 &

# 7. Verify app is running
sleep 3 && lsof -i :8050
# Should show Python processes on port 8050

# 8. Check logs for errors
tail app.log

# 9. Access app in browser
# http://localhost:8050
```

### 🛑 Safe App Shutdown Process
```bash
# 1. Kill app processes
pkill -f "python app.py"

# 2. Verify app is stopped
lsof -i :8050
# Should return empty

# 3. Deactivate environment (optional)
deactivate
# Prompt should return to: jamesmontoya@Jamess-MacBook-Pro FinancialAgent %
```

## ⚠️ REMEMBER: 
- **Environment verification is CRITICAL**
- **Wrong environment = broken dependencies**
- **Clean prompt = safe to proceed**
- This prevents environment corruption and crashes
