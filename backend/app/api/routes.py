"""
API Routes for Resume Builder System
Handles all HTTP endpoints for resume generation, ATS checking, and file downloads
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from backend.app.models.schemas import ResumeInput, ResumeResponse, ATSCheckInput, ATSScore
from backend.app.services.gemini_service import GeminiService
from backend.app.services.ats_scoring_service import ATSScoringService
from backend.app.services.pdf_service import PDFGenerationService
from backend.app.services.docx_service import DOCXGenerationService
from backend.app.utils.file_processor import FileProcessor
from typing import Optional
import json
import traceback


router = APIRouter()


# Initialize services
gemini_service = GeminiService()
ats_service = ATSScoringService()
pdf_service = PDFGenerationService()
docx_service = DOCXGenerationService()
file_processor = FileProcessor()

@router.post("/generate-resume", response_model=ResumeResponse)
async def generate_resume(
    full_name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    target_role: str = Form(...),
    job_description: Optional[str] = Form(None),
    template: str = Form("professional"),
    user_data_raw: Optional[str] = Form(None),
    existing_resume: Optional[UploadFile] = File(None)
):
    """
    Generate AI-powered ATS-friendly resume
    
    Args:
        full_name: Candidate's full name
        phone: Contact phone number
        email: Contact email
        target_role: Target job position
        job_description: Optional job description for alignment
        template: Resume template (professional/modern/classic)
        user_data_raw: Manual form data from frontend (JSON string)
        existing_resume: Optional existing resume file (PDF/DOCX)
    
    Returns:
        ResumeResponse with generated content and ATS score
    """
    try:
        print(f"\n🔍 DEBUG: Received form data")
        print(f"  - full_name: {full_name}")
        print(f"  - target_role: {target_role}")
        print(f"  - template: {template}")
        print(f"  - user_data_raw length: {len(user_data_raw) if user_data_raw else 0}")
        
        # Parse the manual data from the frontend
        user_data_dict = {}
        existing_resume_text = None
        
        # ─────────────────────────────────────────────────
        # ✅ FIX #1: Process uploaded resume FIRST
        # ─────────────────────────────────────────────────
        if existing_resume:
            # Validate file
            file_content = await existing_resume.read()
            is_valid, error_msg = file_processor.validate_file(
                existing_resume.filename,
                len(file_content)
            )
            
            if not is_valid:
                raise HTTPException(status_code=400, detail=error_msg)
            
            # Extract text
            existing_resume_text = file_processor.process_uploaded_file(
                existing_resume.filename,
                file_content
            )
            
            if not existing_resume_text:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to extract text from uploaded resume"
                )
            
            print(f"📄 Extracted {len(existing_resume_text)} chars from uploaded resume")
            
            # ✅ FIX #2: Parse resume into structured data
            user_data_dict = file_processor.parse_resume_to_structured_data(
                existing_resume_text, full_name, target_role
            )
            print(f"📦 Parsed structured data from resume:")
            print(f"  - Experience: {len(user_data_dict.get('experience', []))}")
            print(f"  - Projects: {len(user_data_dict.get('projects', []))}")
            print(f"  - Certifications: {len(user_data_dict.get('certifications', []))}")
        
        # ✅ FIX #3: Use manual form data if no upload
        elif user_data_raw:
            try:
                user_data_dict = json.loads(user_data_raw)
                print(f"\n📦 Parsed manual user_data:")
                print(f"  - Experience: {len(user_data_dict.get('experience', []))}")
                print(f"  - Education: {len(user_data_dict.get('education', []))}")
                print(f"  - Projects: {len(user_data_dict.get('projects', []))}")
                print(f"  - Certifications: {len(user_data_dict.get('certifications', []))}")
                print(f"  - Achievements: {len(user_data_dict.get('achievements', []))}")
            except json.JSONDecodeError as je:
                print(f"⚠️ Warning: user_data_raw parsing failed: {je}")
                user_data_dict = {}
        
        # Generate resume content using Gemini AI
        print(f"\n🤖 Calling Gemini with user_data...")
        resume_content = gemini_service.generate_resume_content(
            full_name=full_name,
            phone=phone,
            email=email,
            target_role=target_role,
            template=template,
            job_description=job_description,
            existing_resume_text=existing_resume_text,
            user_data=user_data_dict  # ← Now contains structured data from BOTH modes
        )
        
        print(f"\n✅ Resume generated:")
        print(f"  - Experience: {len(resume_content.experience)}")
        print(f"  - Education: {len(resume_content.education)}")
        print(f"  - Projects: {len(resume_content.projects)}")
        print(f"  - Certifications: {len(resume_content.certifications)}")
        
        # Calculate ATS score
        ats_score = ats_service.calculate_ats_score(
            resume_content=resume_content,
            job_description=job_description,
            target_role=target_role
        )
        
        return ResumeResponse(
            success=True,
            resume_content=resume_content,
            ats_score=ats_score,
            message="Resume generated successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in generate_resume route: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error generating resume: {str(e)}"
        )

@router.post("/check-ats-score", response_model=ATSScore)
async def check_ats_score(
    resume_file: UploadFile = File(...),
    job_description: Optional[str] = Form(None),
    target_role: str = Form(...)
):
    """
    Check ATS score of existing resume
    
    Args:
        resume_file: Resume file (PDF/DOCX)
        job_description: Optional job description
        target_role: Target job role
    
    Returns:
        ATSScore with detailed scoring breakdown
    """
    try:
        # Validate and process file
        file_content = await resume_file.read()
        is_valid, error_msg = file_processor.validate_file(
            resume_file.filename,
            len(file_content)
        )
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Extract text
        resume_text = file_processor.process_uploaded_file(
            resume_file.filename,
            file_content
        )
        
        if not resume_text:
            raise HTTPException(
                status_code=400,
                detail="Failed to extract text from resume"
            )
        
        # Generate minimal resume content for ATS scoring
        # Parse the resume text into structured format
        resume_content = gemini_service.generate_resume_content(
            full_name="Resume Owner",
            phone="",
            email="",
            target_role=target_role,
            job_description=job_description,
            existing_resume_text=resume_text,
            user_data={}
        )
        
        # Calculate ATS score
        ats_score = ats_service.calculate_ats_score(
            resume_content=resume_content,
            job_description=job_description,
            target_role=target_role
        )
        
        return ats_score
    
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error checking ATS score: {str(e)}"
        )

@router.post("/download-pdf")
async def download_pdf(resume_data: str = Form(...), template: str = Form("professional")):
    """
    Generate and download resume as PDF
    
    Args:
        resume_data: JSON string of resume content
        template: Template style
    
    Returns:
        PDF file as StreamingResponse
    """
    try:
        # Parse resume data
        resume_dict = json.loads(resume_data)
        from backend.app.models.schemas import ResumeContent
        resume_content = ResumeContent(**resume_dict)
        
        # Generate PDF
        pdf_buffer = pdf_service.generate_pdf(resume_content, template)
        
        # Return as downloadable file
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=resume_{resume_content.full_name.replace(' ', '_')}.pdf"
            }
        )
    
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error generating PDF: {str(e)}"
        )

@router.post("/download-docx")
async def download_docx(resume_data: str = Form(...), template: str = Form("professional")):
    """
    Generate and download resume as DOCX
    
    Args:
        resume_data: JSON string of resume content
        template: Template style
    
    Returns:
        DOCX file as StreamingResponse
    """
    try:
        # Parse resume data
        resume_dict = json.loads(resume_data)
        from backend.app.models.schemas import ResumeContent
        resume_content = ResumeContent(**resume_dict)
        
        # Generate DOCX
        docx_buffer = docx_service.generate_docx(resume_content, template)
        
        # Return as downloadable file
        return StreamingResponse(
            docx_buffer,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename=resume_{resume_content.full_name.replace(' ', '_')}.docx"
            }
        )
    
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error generating DOCX: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Resume Builder API"}
