"""
API Routes for Resume Builder System
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from backend.app.models.schemas import ResumeResponse, ATSScore, ResumeContent
from backend.app.services.gemini_service import GeminiService
from backend.app.services.ats_scoring_service import ATSScoringService
from backend.app.services.pdf_service import PDFGenerationService
from backend.app.services.docx_service import DOCXGenerationService
from backend.app.utils.file_processor import FileProcessor
from typing import Optional
import json

router = APIRouter()

gemini_service = GeminiService()
ats_service    = ATSScoringService()
pdf_service    = PDFGenerationService()
docx_service   = DOCXGenerationService()
file_processor = FileProcessor()


# ── /generate-resume ─────────────────────────────────────────────────────
@router.post("/generate-resume", response_model=ResumeResponse)
async def generate_resume(
    full_name:    str = Form(...),
    phone:        str = Form(...),
    email:        str = Form(...),
    target_role:  str = Form(...),
    template:     str = Form("professional"),
    job_description:   Optional[str]        = Form(None),
    user_data:         Optional[str]        = Form(None),   # JSON blob from multi-step form
    existing_resume:   Optional[UploadFile] = File(None),
):
    try:
        # ── Parse structured user data ────────────────────────────────
        ud: dict = {}
        if user_data:
            try:
                ud = json.loads(user_data)
            except Exception:
                ud = {}

        # ── Extract text from uploaded file (if any) ──────────────────
        existing_text: Optional[str] = None
        if existing_resume and existing_resume.filename:
            file_bytes = await existing_resume.read()
            if file_bytes:
                is_valid, err = file_processor.validate_file(existing_resume.filename, len(file_bytes))
                if not is_valid:
                    raise HTTPException(status_code=400, detail=err)
                existing_text = file_processor.process_uploaded_file(
                    existing_resume.filename, file_bytes
                )

        # ── Call AI ───────────────────────────────────────────────────
        resume_content = gemini_service.generate_resume_content(
            full_name=full_name,
            phone=phone,
            email=email,
            target_role=target_role,
            job_description=job_description,
            existing_resume_text=existing_text,
            user_data=ud,
        )

        # ── ATS scoring ───────────────────────────────────────────────
        ats_score = ats_service.calculate_ats_score(
            resume_content=resume_content,
            job_description=job_description,
            target_role=target_role,
        )

        return ResumeResponse(
            success=True,
            resume_content=resume_content,
            ats_score=ats_score,
            message="Resume generated successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating resume: {str(e)}")


# ── /check-ats-score ─────────────────────────────────────────────────────
@router.post("/check-ats-score", response_model=ATSScore)
async def check_ats_score(
    resume_file:     UploadFile       = File(...),
    target_role:     str              = Form(...),
    job_description: Optional[str]   = Form(None),
):
    try:
        file_bytes = await resume_file.read()
        is_valid, err = file_processor.validate_file(resume_file.filename, len(file_bytes))
        if not is_valid:
            raise HTTPException(status_code=400, detail=err)

        resume_text = file_processor.process_uploaded_file(resume_file.filename, file_bytes)
        if not resume_text:
            raise HTTPException(status_code=400, detail="Could not extract text from the uploaded file.")

        resume_content = gemini_service.generate_resume_content(
            full_name="Resume Owner",
            phone="",
            email="",
            target_role=target_role,
            job_description=job_description,
            existing_resume_text=resume_text,
            user_data=None,
        )

        return ats_service.calculate_ats_score(
            resume_content=resume_content,
            job_description=job_description,
            target_role=target_role,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking ATS score: {str(e)}")


# ── /download-pdf ─────────────────────────────────────────────────────────
@router.post("/download-pdf")
async def download_pdf(
    resume_data: str = Form(...),
    template:    str = Form("professional"),
):
    try:
        rc = ResumeContent(**json.loads(resume_data))
        buf = pdf_service.generate_pdf(rc, template)
        fname = f"resume_{rc.full_name.replace(' ', '_')}.pdf"
        return StreamingResponse(
            buf,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={fname}"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation error: {e}")


# ── /download-docx ────────────────────────────────────────────────────────
@router.post("/download-docx")
async def download_docx(
    resume_data: str = Form(...),
    template:    str = Form("professional"),
):
    try:
        rc = ResumeContent(**json.loads(resume_data))
        buf = docx_service.generate_docx(rc, template)
        fname = f"resume_{rc.full_name.replace(' ', '_')}.docx"
        return StreamingResponse(
            buf,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={fname}"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DOCX generation error: {e}")


# ── /health ───────────────────────────────────────────────────────────────
@router.get("/health")
async def health():
    return {"status": "healthy", "service": "Resume Builder API"}