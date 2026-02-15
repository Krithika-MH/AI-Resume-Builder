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
        existing_resume: Optional existing resume file (PDF/DOCX)
    
    Returns:
        ResumeResponse with generated content and ATS score
    """
    try:
        # Process existing resume if uploaded
        existing_resume_text = None
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
        
        # Generate resume content using Gemini AI
        resume_content = gemini_service.generate_resume_content(
            full_name=full_name,
            phone=phone,
            email=email,
            target_role=target_role,
            job_description=job_description,
            existing_resume_text=existing_resume_text
        )
        
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
            existing_resume_text=resume_text
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
        raise HTTPException(
            status_code=500,
            detail=f"Error generating DOCX: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Resume Builder API"}