# AI-Based ATS-Friendly Resume Creation System

## 🎯 Project Overview

A production-grade AI-powered resume builder that creates ATS-optimized resumes using Google's Gemini AI. This system provides comprehensive resume generation, editing capabilities, ATS scoring, and multiple download formats (PDF/DOCX).

### Key Features

✅ **AI-Powered Generation** - Uses Gemini AI for intelligent resume content creation  
✅ **ATS Optimization** - Industry-standard scoring algorithm (0-100)  
✅ **Multiple Templates** - Professional, Modern, and Classic designs  
✅ **Live Editing** - Edit resume content like a word processor  
✅ **Multiple Formats** - Download as PDF or editable DOCX  
✅ **Job Description Alignment** - Keyword matching and optimization  
✅ **Existing Resume Import** - Upload and improve existing resumes  
✅ **Standalone ATS Checker** - Dedicated page for checking resume scores  

---

## 📁 Project Structure

```
D:\Resume Builder\
├── backend/
│   └── app/
│       ├── api/
│       │   ├── __init__.py
│       │   └── routes.py              # API endpoints
│       ├── core/
│       │   ├── __init__.py
│       │   └── config.py              # Configuration & settings
│       ├── models/
│       │   ├── __init__.py
│       │   └── schemas.py             # Pydantic models
│       ├── services/
│       │   ├── __init__.py
│       │   ├── gemini_service.py      # Gemini AI integration
│       │   ├── ats_scoring_service.py # ATS scoring logic
│       │   ├── pdf_service.py         # PDF generation
│       │   └── docx_service.py        # DOCX generation
│       ├── utils/
│       │   ├── __init__.py
│       │   └── file_processor.py      # File upload handling
│       └── main.py                    # FastAPI application
├── frontend/
│   ├── pages/
│   │   ├── resume-builder.html        # Resume builder page
│   │   └── ats-checker.html           # ATS checker page
│   ├── static/
│   │   └── js/
│   │       ├── resume-builder.js      # Resume builder logic
│   │       └── ats-checker.js         # ATS checker logic
│   └── index.html                     # Home page
├── .env                                # Environment variables (create this)
├── .env.example                        # Environment template
├── requirements.txt                    # Python dependencies
└── README.md                           # This file
```

---

## 🚀 Setup Instructions (Windows)

### Prerequisites

- Python 3.8 or higher
- VS Code (recommended)
- Google Gemini API key

### Step 1: Navigate to Project Directory

Open VS Code terminal (Ctrl + `) and run:

```bash
cd "D:\Resume Builder"
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
```

### Step 3: Activate Virtual Environment

```bash
venv\Scripts\activate
```

You should see `(venv)` prefix in your terminal.

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Setup Environment Variables

1. Copy `.env.example` to create `.env`:

```bash
copy .env.example .env
```

2. Open `.env` file and add your Gemini API key:

```
GEMINI_API_KEY=your_actual_gemini_api_key_here
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=True
```

**Get your Gemini API key:**
- Visit: https://makersuite.google.com/app/apikey
- Sign in with Google account
- Click "Create API Key"
- Copy the key and paste it in your `.env` file

### Step 6: Run the Application

```bash
python backend/app/main.py
```

Or using uvicorn directly:

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 7: Access the Application

Open your web browser and navigate to:

- **Home Page**: http://localhost:8000
- **Resume Builder**: http://localhost:8000/pages/resume-builder.html
- **ATS Checker**: http://localhost:8000/pages/ats-checker.html
- **API Docs**: http://localhost:8000/docs

---

## 📖 How to Use

### Building a Resume

1. Go to **Resume Builder** page
2. Fill in required information:
   - Full Name
   - Phone Number
   - Email
   - Target Job Role
3. (Optional) Add job description for better alignment
4. (Optional) Upload existing resume (PDF/DOCX)
5. Select template (Professional/Modern/Classic)
6. Click **"Generate Resume"**
7. Edit the generated content directly in the preview
8. Download as PDF or DOCX

### Checking ATS Score

1. Go to **ATS Checker** page
2. Upload your resume (PDF/DOCX)
3. Enter target job role
4. (Optional) Add job description for better keyword matching
5. Click **"Check ATS Score"**
6. Review detailed score breakdown and suggestions

---

## 🔧 Technical Details

### AI Integration - Gemini Prompt Engineering

The system uses carefully engineered prompts for Gemini AI:

**Prompt Strategy:**
- Structured instructions with clear sections
- Industry-standard action verbs list
- Quantifiable metrics emphasis
- ATS-friendly formatting guidelines
- JSON output format for reliable parsing

**Key Elements:**
1. Context setting (expert resume writer)
2. Candidate information injection
3. Job description alignment
4. Section-by-section requirements
5. Format specifications (JSON)
6. Quality metrics (action verbs, numbers)

### ATS Scoring Algorithm

The ATS score (0-100) is calculated using weighted components:

**Score Components:**
1. **Skill Match (25%)** - Compares resume skills with JD requirements
2. **Keyword Relevance (25%)** - Analyzes keyword overlap with JD
3. **Role Alignment (20%)** - Checks role mentions, action verbs, metrics
4. **Formatting (15%)** - Validates ATS-friendly formatting
5. **Section Completeness (15%)** - Ensures all required sections present

**Industry Standards Applied:**
- Action verb usage (Developed, Implemented, Led, etc.)
- Quantifiable achievements (percentages, numbers)
- Standard sections (Summary, Skills, Experience, Education)
- Clean formatting (no special characters, tables, graphics)

### File Generation

**PDF Generation (ReportLab):**
- Professional typography
- Proper spacing and margins
- ATS-friendly formatting
- Multiple template support

**DOCX Generation (python-docx):**
- Editable Word documents
- Consistent styling
- Proper heading hierarchy
- Table-free layout

---

## 🌐 Deployment

### Local Deployment

Already covered in Setup Instructions above.

### Production Deployment Options

#### Option 1: Railway.app

1. Create account on Railway.app
2. Connect GitHub repository
3. Add environment variables in Railway dashboard
4. Deploy automatically

#### Option 2: Render.com

1. Create account on Render.com
2. Create new Web Service
3. Connect repository
4. Set environment variables
5. Deploy

#### Option 3: Heroku

1. Install Heroku CLI
2. Login: `heroku login`
3. Create app: `heroku create resume-builder-app`
4. Set config: `heroku config:set GEMINI_API_KEY=your_key`
5. Deploy: `git push heroku main`

#### Option 4: Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t resume-builder .
docker run -p 8000:8000 --env-file .env resume-builder
```

---

## 🧪 Testing

### Test API Endpoints

**Health Check:**
```bash
curl http://localhost:8000/api/health
```

**Generate Resume:**
```bash
curl -X POST http://localhost:8000/api/generate-resume \
  -F "full_name=John Doe" \
  -F "phone=+1234567890" \
  -F "email=john@example.com" \
  -F "target_role=Software Engineer"
```

### Manual Testing Checklist

- [ ] Home page loads correctly
- [ ] Resume builder form validation works
- [ ] AI generates resume content
- [ ] ATS score displays correctly
- [ ] Resume editor allows editing
- [ ] PDF download works
- [ ] DOCX download works
- [ ] File upload (PDF/DOCX) works
- [ ] ATS checker analyzes resumes
- [ ] Error handling displays properly

---

## 🐛 Troubleshooting

### Common Issues

**Issue: "GEMINI_API_KEY is not set"**
- Solution: Check `.env` file exists and has valid API key

**Issue: "Module not found" errors**
- Solution: Ensure virtual environment is activated and dependencies installed

**Issue: "Port 8000 already in use"**
- Solution: Change port in `.env` or kill process using port 8000

**Issue: API returns 500 errors**
- Solution: Check terminal logs for detailed error messages

**Issue: Resume generation fails**
- Solution: Verify Gemini API key is valid and has quota

---

## 📝 API Documentation

### Endpoints

#### POST `/api/generate-resume`

Generate AI-powered resume.

**Parameters:**
- `full_name` (string, required)
- `phone` (string, required)
- `email` (string, required)
- `target_role` (string, required)
- `job_description` (string, optional)
- `template` (string, default: "professional")
- `existing_resume` (file, optional)

**Response:**
```json
{
  "success": true,
  "resume_content": {...},
  "ats_score": {...},
  "message": "Resume generated successfully"
}
```

#### POST `/api/check-ats-score`

Check ATS score of existing resume.

**Parameters:**
- `resume_file` (file, required)
- `target_role` (string, required)
- `job_description` (string, optional)

**Response:**
```json
{
  "overall_score": 85,
  "skill_match": 90,
  "keyword_relevance": 85,
  "role_alignment": 80,
  "formatting_score": 90,
  "section_completeness": 80,
  "explanation": "...",
  "missing_keywords": [...],
  "suggestions": [...]
}
```

#### POST `/api/download-pdf`

Download resume as PDF.

#### POST `/api/download-docx`

Download resume as DOCX.

---

## 🎓 Project Highlights

### What Makes This Production-Grade?

1. **Modular Architecture** - Clean separation of concerns
2. **Error Handling** - Comprehensive error management
3. **Input Validation** - Pydantic models for data validation
4. **Security** - Environment variables for sensitive data
5. **Scalability** - FastAPI async support
6. **Documentation** - Comprehensive code comments
7. **User Experience** - Modern, responsive UI
8. **Professional Output** - Industry-standard resume formats

### Technologies Used

**Backend:**
- FastAPI - Modern, fast web framework
- Google Gemini AI - Advanced language model
- ReportLab - PDF generation
- python-docx - DOCX generation
- Pydantic - Data validation

**Frontend:**
- HTML5
- Tailwind CSS - Modern styling
- Vanilla JavaScript - No framework overhead

---

## 📄 License

This project is created for the Sophyra Platform AI Intern Qualification Task.

---

## 👤 Author

Developed as part of AI Intern Qualification Task for Sophyra Platform.

---

## 📧 Support

For issues or questions, please check the troubleshooting section or review the code comments for detailed explanations.

---

**Note:** Remember to never commit your `.env` file with actual API keys to version control. Always use `.env.example` as a template.