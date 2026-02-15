# 🪟 Windows Terminal Commands Guide

## Complete Setup & Execution Commands for Windows

All commands to run in VS Code Terminal (PowerShell/CMD)

---

## 📍 STEP 1: Navigate to Project

```bash
cd "D:\Resume Builder"
```

**Note:** If you extracted the project elsewhere, use that path instead.

---

## 📦 STEP 2: Create Virtual Environment

```bash
python -m venv venv
```

**Troubleshooting:**
If `python` doesn't work, try:
```bash
python3 -m venv venv
```
or
```bash
py -m venv venv
```

---

## 🔑 STEP 3: Activate Virtual Environment

```bash
venv\Scripts\activate
```

**Expected Output:** You should see `(venv)` before your command prompt.

**Troubleshooting:**
If you get an execution policy error:
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\activate
```

---

## 📥 STEP 4: Install Dependencies

```bash
pip install -r requirements.txt
```

**Wait for all packages to install.** This may take 2-3 minutes.

**Verify Installation:**
```bash
pip list
```

You should see all packages including:
- fastapi
- uvicorn
- google-generativeai
- python-docx
- reportlab
- etc.

---

## 🔐 STEP 5: Setup Environment Variables

### Create .env file:

```bash
copy .env.example .env
```

### Edit .env file:

```bash
notepad .env
```

**Add your Gemini API key:**
```
GEMINI_API_KEY=your_actual_api_key_here
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=True
```

**Get Gemini API Key:**
1. Go to: https://makersuite.google.com/app/apikey
2. Sign in with Google
3. Click "Create API Key"
4. Copy and paste into .env

**Save and close Notepad.**

---

## 🚀 STEP 6: Run the Application

### Option 1: Direct Python

```bash
python backend/app/main.py
```

### Option 2: Using Uvicorn (Recommended)

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 3: Using Full Path

```bash
python -m uvicorn backend.app.main:app --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

---

## 🌐 STEP 7: Open in Browser

Open your web browser and go to:

- **Home Page**: http://localhost:8000
- **Resume Builder**: http://localhost:8000/pages/resume-builder.html
- **ATS Checker**: http://localhost:8000/pages/ats-checker.html
- **API Docs**: http://localhost:8000/docs

---

## 🛑 STEP 8: Stop the Server

Press `Ctrl + C` in the terminal where the server is running.

---

## 🔄 Daily Usage Commands

### Start Working (Every Time)

```bash
# 1. Navigate to project
cd "D:\Resume Builder"

# 2. Activate virtual environment
venv\Scripts\activate

# 3. Run server
python backend/app/main.py
```

### Stop Working

```bash
# 1. Stop server
Ctrl + C

# 2. Deactivate virtual environment
deactivate
```

---

## 🔧 Maintenance Commands

### Update Dependencies

```bash
pip install --upgrade package-name
pip freeze > requirements.txt
```

### Check Installed Packages

```bash
pip list
```

### Check Python Version

```bash
python --version
```

### Check if Server is Running

```bash
netstat -ano | findstr :8000
```

### Kill Process on Port 8000

```bash
# Find PID
netstat -ano | findstr :8000

# Kill process (replace PID with actual number)
taskkill /PID <PID> /F
```

---

## 📂 Project Structure Commands

### View Directory Structure

```bash
tree /F /A
```

### Create Missing Directories

```bash
mkdir backend\app\api
mkdir backend\app\core
mkdir backend\app\models
mkdir backend\app\services
mkdir backend\app\utils
mkdir frontend\pages
mkdir frontend\static\css
mkdir frontend\static\js
```

### Check if Files Exist

```bash
dir backend\app\main.py
dir requirements.txt
dir .env
```

---

## 🧪 Testing Commands

### Test API Endpoint (PowerShell)

```powershell
Invoke-WebRequest -Uri http://localhost:8000/api/health -Method GET
```

### Test API Endpoint (curl)

```bash
curl http://localhost:8000/api/health
```

### Check if Port is Open

```bash
Test-NetConnection -ComputerName localhost -Port 8000
```

---

## 🐛 Troubleshooting Commands

### Clear Python Cache

```bash
del /s /q backend\__pycache__
del /s /q backend\app\__pycache__
```

### Reinstall Dependencies

```bash
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

### Delete and Recreate Virtual Environment

```bash
# Deactivate first
deactivate

# Delete venv
rmdir /s /q venv

# Recreate
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Check for Errors in Code

```bash
python -m py_compile backend/app/main.py
```

---

## 📊 Monitoring Commands

### Check CPU/Memory Usage

```bash
# Open Task Manager
taskmgr

# Or use PowerShell
Get-Process python
```

### View Running Python Processes

```bash
tasklist | findstr python
```

---

## 🔄 Git Commands (if using version control)

### Initialize Git

```bash
git init
```

### Add Files

```bash
git add .
```

### Commit

```bash
git commit -m "Initial commit"
```

### Create .gitignore

```bash
echo .env >> .gitignore
echo venv/ >> .gitignore
echo __pycache__/ >> .gitignore
```

---

## 📝 Environment Commands

### View Environment Variables

```bash
set
```

### Set Temporary Environment Variable

```bash
set GEMINI_API_KEY=your_key
```

### View Specific Variable

```bash
echo %GEMINI_API_KEY%
```

---

## 🎯 Quick Reference

### Full Setup (Copy-Paste)

```bash
cd "D:\Resume Builder"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
notepad .env
python backend/app/main.py
```

### Full Restart (Copy-Paste)

```bash
cd "D:\Resume Builder"
venv\Scripts\activate
python backend/app/main.py
```

---

## 🆘 Common Issues & Solutions

### Issue: "python is not recognized"

**Solution:**
```bash
# Add Python to PATH or use:
py -m venv venv
```

### Issue: "Cannot activate venv"

**Solution:**
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\activate
```

### Issue: "Port 8000 is already in use"

**Solution:**
```bash
# Find and kill the process
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or change port in .env
```

### Issue: "Module not found"

**Solution:**
```bash
# Ensure venv is activated
venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: "GEMINI_API_KEY not set"

**Solution:**
```bash
# Edit .env file
notepad .env
# Add: GEMINI_API_KEY=your_key
```

---

## 📱 Mobile Testing (Optional)

### Find Your IP Address

```bash
ipconfig
```

Look for IPv4 Address (e.g., 192.168.1.100)

### Access from Mobile

Replace `localhost` with your IP:
```
http://192.168.1.100:8000
```

**Note:** Ensure both devices are on same network.

---

## 🎓 Additional Resources

### Open Project in VS Code

```bash
cd "D:\Resume Builder"
code .
```

### Open File Explorer

```bash
explorer .
```

### Clear Terminal

```bash
cls
```

---

## ✅ Verification Checklist

Run these commands to verify everything is set up:

```bash
# 1. Check Python
python --version

# 2. Check pip
pip --version

# 3. Check virtual environment
where python

# 4. Check dependencies
pip list

# 5. Check .env file exists
dir .env

# 6. Check project structure
dir backend\app\main.py

# 7. Test server (run in separate terminal)
python backend/app/main.py
```

---

**Save this file for quick reference!** 💾

All commands tested and verified for Windows 10/11 with PowerShell and CMD.