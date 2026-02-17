"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict

class ResumeInput(BaseModel):
    """Input model for resume generation"""
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=10, max_length=20)
    email: EmailStr
    target_role: str = Field(..., min_length=2, max_length=100)
    job_description: Optional[str] = None
    existing_resume_text: Optional[str] = None
    template: str = Field(default="professional", pattern="^(professional|modern|classic)$")

# ==============================
# Structured Nested Models
# ==============================

class ContactInfo(BaseModel):
    """Contact information"""
    phone: str
    email: str
    linkedin: Optional[str] = ""
    github: Optional[str] = ""
    portfolio: Optional[str] = ""

class ExperienceItem(BaseModel):
    """Single work experience entry"""
    title: str
    company: str
    duration: str
    location: str
    responsibilities: List[str]

class EducationItem(BaseModel):
    """Single education entry"""
    degree: str
    institution: str
    year: str
    gpa: Optional[str] = None

class ProjectItem(BaseModel):
    """Single project entry"""
    name: str
    description: str
    technologies: str
    impact: str

# ==============================
# Main Resume Content Model
# ==============================

class ResumeContent(BaseModel):
    """Structured resume content"""
    full_name: str
    contact: ContactInfo
    summary: str
    skills: List[str]
    experience: List[ExperienceItem]
    education: List[EducationItem]
    projects: List[ProjectItem]
    certifications: List[str]
    achievements: List[str]

# ==============================
# ATS Scoring Models
# ==============================

class ATSScore(BaseModel):
    """ATS scoring result"""
    overall_score: int = Field(..., ge=0, le=100)
    skill_match: int = Field(..., ge=0, le=100)
    keyword_relevance: int = Field(..., ge=0, le=100)
    role_alignment: int = Field(..., ge=0, le=100)
    formatting_score: int = Field(..., ge=0, le=100)
    section_completeness: int = Field(..., ge=0, le=100)
    action_verb_score: Optional[int] = None
    quantified_score: Optional[int] = None
    faang_compliance: Optional[int] = None
    explanation: str
    missing_keywords: List[str]
    suggestions: List[str]

class ResumeResponse(BaseModel):
    """Complete resume generation response"""
    success: bool
    resume_content: ResumeContent
    ats_score: ATSScore
    message: str

class ATSCheckInput(BaseModel):
    """Input for standalone ATS check"""
    resume_text: str
    job_description: Optional[str] = None
    target_role: str