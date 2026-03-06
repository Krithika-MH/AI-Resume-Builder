<div align="center">

<table>
  <tr>
    <td><img src="frontend/static/images/ResumeWise - logo.png" alt="ResumeWise AI Logo" width="120"/></td>
    <td>
      <h1>ResumeWise AI</h1>
      <h3>✦ AI-Powered · Industry Grade ATS Scoring</h3>
      <p><b>Smarter Resumes. Stronger Careers.</b><br/>
      Build ATS-optimized resumes using real Gemini AI — your facts, polished to perfection.<br/>
      Score against FAANG standards in seconds.</p>
      <a href="#-quick-start"><b>✨ Build My Resume</b></a>
    </td>
  </tr>
</table>

---

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Gemini AI](https://img.shields.io/badge/Gemini%20AI-8E75B2?style=for-the-badge&logo=googlegemini)](https://ai.google.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css)](https://tailwindcss.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

</div>

## 📺 Project Demo
Watch ResumeWise AI in action. This video covers AI generation, the live inline editor, and the FAANG-grade ATS scoring engine.

<div align="center">
  <a href="https://youtu.be/3A-MAoaB8aA">
    <img src="https://img.youtube.com/vi/3A-MAoaB8aA/maxresdefault.jpg" alt="ResumeWise AI Demo Video" width="800" style="border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
    <br/>
    <b>▶ Click to Watch Demo on YouTube</b>
  </a>
</div>

---

## 🎯 Overview
**ResumeWise AI** is a production-grade AI resume builder that bridges the gap between candidate experience and recruiter expectations. By combining **Google Gemini 2.5 Flash** with a specialized scoring engine, it ensures your resume isn't just a document, but a competitive asset.

### Why ResumeWise?
* 🤖 **AI-Powered Polishing:** Leverages LLMs to turn dry bullet points into high-impact achievement statements.
* 📊 **FAANG-Grade Scoring:** 8-component scoring logic aligned with Google, Meta, and Amazon recruitment patterns.
* 🔄 **Smart Extraction:** Upload a PDF/DOCX and let the AI restructure it into a modern layout instantly.
* ✅ **ATS Scoring vs Job Descriptions**

---

## ✨ Key Features

| Feature | Description |
| :--- | :--- |
| **ATS Scoring Engine** | Multi-dimensional analysis: Skill Match, Action Verbs, and Quantified Impact. |
| **Live Preview** | Real-time editable preview with 12+ industry-standard fonts. |
| **Template Engine** | Switch between **Professional**, **Modern (FAANG)**, and **Classic** layouts. |
| **JD Alignment** | Paste a job description to see missing keywords and tailor your content. |
| **Multi-Format Export** | Download pixel-perfect PDFs and editable DOCX files. |

---

## 🛠️ Tech Stack

**Backend:** * **FastAPI:** High-performance asynchronous Python framework.
* **Google Gemini 2.5 Flash:** State-of-the-art AI for content optimization.
* **ReportLab & python-docx:** Professional document generation.

**Frontend:**
* **Vanilla JavaScript:** Lightweight, fast, and responsive UI logic.
* **Tailwind CSS:** Modern utility-first styling.
* **Lucide Icons:** Clean, consistent iconography.

---

## 📈 ATS Scoring Breakdown
Our algorithm weights your resume based on technical standards used by top-tier firms:

| Metric | Weight | Focus Area |
| :--- | :--- | :--- |
| **Skill Match** | 20% | Alignment with FAANG-critical hard skills. |
| **Keyword Relevance** | 18% | Industry-specific terminology density. |
| **Role Alignment** | 15% | Experience relevance to the target position. |
| **Action Verbs** | 10% | Use of strong engineering and leadership verbs. |
| **Quantified Impact**| 10% | Presence of metrics (%, $, users, latency). |
| **Formatting** | 10% | ATS readability and structure. |

---

## 📦 Installation & Quick Start

### 1. Prerequisites
* Python 3.11+
* Google Gemini API Key ([Get it here](https://aistudio.google.com/))

### 2. Setup
```bash
# Clone the repository
git clone [https://github.com/yourusername/resumewise-ai.git](https://github.com/yourusername/resumewise-ai.git)
cd resumewise-ai

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
