# ⚡ Quick Start Guide

## Setup in 5 Minutes

### 1. Open VS Code Terminal

Press `Ctrl + ~` or go to Terminal > New Terminal

### 2. Navigate to Project

```bash
cd "D:\Resume Builder"
```

### 3. Create & Activate Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Setup Environment Variables

```bash
copy .env.example .env
```

Then open `.env` and add your Gemini API key:

```
GEMINI_API_KEY=your_key_here
```

**Get API Key:** https://makersuite.google.com/app/apikey

### 6. Run the Application

```bash
python backend/app/main.py
```

### 7. Open in Browser

Go to: http://localhost:8000

---

## 🎯 What You Can Do

### Build Resume
1. Click "Resume Builder"
2. Fill in your details
3. (Optional) Upload existing resume
4. Click "Generate Resume"
5. Edit the content
6. Download PDF or DOCX

### Check ATS Score
1. Click "ATS Checker"
2. Upload your resume
3. Enter target role
4. (Optional) Add job description
5. Click "Check ATS Score"
6. Review suggestions

---

## 🔑 Key Commands

### Start Server
```bash
python backend/app/main.py
```

### Alternative Start (with auto-reload)
```bash
uvicorn backend.app.main:app --reload
```

### Install New Package
```bash
pip install package-name
pip freeze > requirements.txt
```

### Deactivate Virtual Environment
```bash
deactivate
```

---

## 📱 Access Points

- **Home**: http://localhost:8000
- **Resume Builder**: http://localhost:8000/pages/resume-builder.html
- **ATS Checker**: http://localhost:8000/pages/ats-checker.html
- **API Docs**: http://localhost:8000/docs

---

## ⚠️ Common Issues

**Virtual environment not activating?**
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\activate
```

**Port already in use?**
Change port in `.env`:
```
APP_PORT=8001
```

**Module not found?**
```bash
pip install -r requirements.txt
```

---

## 📊 Project Structure (Simplified)

```
Resume Builder/
├── backend/        # Python FastAPI backend
├── frontend/       # HTML/CSS/JS frontend
├── .env           # Your API keys (create this!)
└── requirements.txt
```

---

## 🎓 Features

✅ AI-powered resume generation  
✅ ATS score calculation (0-100)  
✅ Live editing capability  
✅ PDF & DOCX downloads  
✅ Multiple templates  
✅ Job description alignment  

---

That's it! You're ready to build professional resumes! 🚀