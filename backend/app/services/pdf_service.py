"""
PDF Generation Service – 3 visually distinct templates.
FIXED: Proper spacing, no overlaps, clean layout
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, KeepTogether
)
from reportlab.lib import colors
from backend.app.models.schemas import ResumeContent
from io import BytesIO
from typing import List


# ── Colour palette ─────────────────────────────────────────
NAVY   = colors.HexColor('#1E3A4C')
GREEN  = colors.HexColor('#2E7D52')
BLACK  = colors.HexColor('#111111')
DGRAY  = colors.HexColor('#444444')
LGRAY  = colors.HexColor('#888888')


class PDFGenerationService:

    def generate_pdf(self, resume_content: ResumeContent, template: str = "professional") -> BytesIO:
        buf = BytesIO()
        if template == "modern":
            builder = ModernTemplate()
        elif template == "classic":
            builder = ClassicTemplate()
        else:
            builder = ProfessionalTemplate()

        doc = SimpleDocTemplate(
            buf, pagesize=letter,
            rightMargin=builder.margin, leftMargin=builder.margin,
            topMargin=builder.margin, bottomMargin=builder.margin,
        )
        doc.build(builder.build(resume_content))
        buf.seek(0)
        return buf


# ═══════════════════════════════════════════════════════════
#  TEMPLATE 1 — PROFESSIONAL (FIXED SPACING)
# ═══════════════════════════════════════════════════════════
class ProfessionalTemplate:
    margin = 0.6 * inch

    def __init__(self):
        ss = getSampleStyleSheet()
        def s(name, **kw):
            return ParagraphStyle(name=name, parent=ss['Normal'], **kw)

        # FIXED: Reduced font sizes and spacing for better fit
        self.name     = s('P_Name',  fontSize=20, fontName='Helvetica-Bold',
                          textColor=BLACK, alignment=TA_CENTER, 
                          spaceAfter=2, spaceBefore=0, leading=24)
        
        self.contact  = s('P_Cont',  fontSize=9, fontName='Helvetica',
                          textColor=DGRAY, alignment=TA_CENTER, 
                          spaceAfter=6, spaceBefore=0, leading=11)
        
        self.sec_hdr  = s('P_Sec',   fontSize=10, fontName='Helvetica-Bold',
                          textColor=BLACK, 
                          spaceBefore=8, spaceAfter=3, leading=12)
        
        self.job_ttl  = s('P_Jttl',  fontSize=10, fontName='Helvetica-Bold',
                          textColor=BLACK, 
                          spaceAfter=1, spaceBefore=0, leading=12)
        
        self.sub      = s('P_Sub',   fontSize=9, fontName='Helvetica-Oblique',
                          textColor=LGRAY, 
                          spaceAfter=2, spaceBefore=0, leading=11)
        
        self.body     = s('P_Body',  fontSize=9.5, fontName='Helvetica',
                          textColor=BLACK, 
                          leading=12, spaceAfter=4, spaceBefore=0)
        
        self.bullet   = s('P_Bul',   fontSize=9, fontName='Helvetica',
                          textColor=BLACK, leftIndent=12, 
                          spaceAfter=2, spaceBefore=0, leading=11,
                          bulletIndent=0, firstLineIndent=0)

    def divider(self):
        return HRFlowable(width="100%", thickness=0.5, 
                         color=colors.HexColor('#CCCCCC'), 
                         spaceAfter=3, spaceBefore=0)

    def section(self, title):
        return [
            Spacer(1, 0.05*inch),
            Paragraph(title.upper(), self.sec_hdr),
            self.divider(),
        ]

    def build(self, rc: ResumeContent) -> List:
        st = []

        # Header
        st.append(Paragraph(rc.full_name, self.name))
        cp = _contact_parts(rc)
        if cp: 
            st.append(Paragraph(' | '.join(cp), self.contact))
        st.append(Spacer(1, 0.08*inch))

        # Summary
        if rc.summary:
            st += self.section('Professional Summary')
            st.append(Paragraph(rc.summary, self.body))

        # Skills
        if rc.skills:
            st += self.section('Skills')
            st.append(Paragraph(', '.join(rc.skills), self.body))

        # Experience
        if rc.experience:
            st += self.section('Professional Experience')
            for exp in rc.experience:
                blk = []
                blk.append(Paragraph(exp.title, self.job_ttl))
                
                sub_parts = [exp.company, exp.duration]
                if exp.location: sub_parts.append(exp.location)
                blk.append(Paragraph(' | '.join(sub_parts), self.sub))
                
                for r in (exp.responsibilities or []):
                    blk.append(Paragraph(f'• {r}', self.bullet))
                
                blk.append(Spacer(1, 0.05*inch))
                st.append(KeepTogether(blk))

        # Education
        if rc.education:
            st += self.section('Education')
            for edu in rc.education:
                blk = [Paragraph(edu.degree, self.job_ttl)]
                
                sub_parts = [edu.institution, edu.year]
                if edu.gpa: sub_parts.append(f'GPA: {edu.gpa}')
                blk.append(Paragraph(' | '.join(sub_parts), self.sub))
                
                blk.append(Spacer(1, 0.04*inch))
                st.append(KeepTogether(blk))

        # Projects
        if rc.projects:
            st += self.section('Projects')
            for p in rc.projects:
                blk = [Paragraph(p.name, self.job_ttl)]
                
                if p.technologies:
                    blk.append(Paragraph(f'Technologies: {p.technologies}', self.sub))
                if p.description:
                    blk.append(Paragraph(f'• {p.description}', self.bullet))
                if p.impact:
                    blk.append(Paragraph(f'• {p.impact}', self.bullet))
                
                blk.append(Spacer(1, 0.04*inch))
                st.append(KeepTogether(blk))

        # Certifications
        if rc.certifications:
            st += self.section('Certifications')
            for c in rc.certifications:
                if c and c.strip():
                    st.append(Paragraph(f'• {c}', self.bullet))
            st.append(Spacer(1, 0.04*inch))

        # Achievements
        if rc.achievements:
            st += self.section('Achievements')
            for a in rc.achievements:
                if a and a.strip():
                    st.append(Paragraph(f'• {a}', self.bullet))

        return st


# ═══════════════════════════════════════════════════════════
#  TEMPLATE 2 — MODERN (FIXED SPACING)
# ═══════════════════════════════════════════════════════════
class ModernTemplate:
    margin = 0.55 * inch

    def __init__(self):
        ss = getSampleStyleSheet()
        def s(name, **kw):
            return ParagraphStyle(name=name, parent=ss['Normal'], **kw)

        self.name     = s('M_Name',  fontSize=22, fontName='Helvetica-Bold',
                          textColor=NAVY, alignment=TA_LEFT, 
                          spaceAfter=1, spaceBefore=0, leading=26)
        
        self.contact  = s('M_Cont',  fontSize=9, fontName='Helvetica',
                          textColor=DGRAY, alignment=TA_LEFT, 
                          spaceAfter=8, spaceBefore=0, leading=11)
        
        self.sec_hdr  = s('M_Sec',   fontSize=10.5, fontName='Helvetica-Bold',
                          textColor=GREEN, 
                          spaceBefore=9, spaceAfter=2, leading=13)
        
        self.job_ttl  = s('M_Jttl',  fontSize=10.5, fontName='Helvetica-Bold',
                          textColor=NAVY, 
                          spaceAfter=1, spaceBefore=0, leading=13)
        
        self.sub      = s('M_Sub',   fontSize=9, fontName='Helvetica',
                          textColor=LGRAY, 
                          spaceAfter=2, spaceBefore=0, leading=11)
        
        self.body     = s('M_Body',  fontSize=9.5, fontName='Helvetica',
                          textColor=BLACK, 
                          leading=12, spaceAfter=4, spaceBefore=0)
        
        self.bullet   = s('M_Bul',   fontSize=9, fontName='Helvetica',
                          textColor=BLACK, leftIndent=12, 
                          spaceAfter=2, spaceBefore=0, leading=11,
                          bulletIndent=0, firstLineIndent=0)

    def green_line(self):
        return HRFlowable(width="100%", thickness=2.5, 
                         color=GREEN, spaceAfter=5, spaceBefore=0)

    def section(self, title):
        return [
            Spacer(1, 0.05*inch),
            Paragraph(title.upper(), self.sec_hdr),
            HRFlowable(width="100%", thickness=1, 
                      color=colors.HexColor('#D1E8DB'), 
                      spaceAfter=3, spaceBefore=0),
        ]

    def build(self, rc: ResumeContent) -> List:
        st = []

        # Header
        st.append(Paragraph(rc.full_name, self.name))
        st.append(self.green_line())
        
        cp = _contact_parts(rc)
        if cp: 
            st.append(Paragraph('  ·  '.join(cp), self.contact))

        # Summary
        if rc.summary:
            st += self.section('Profile')
            st.append(Paragraph(rc.summary, self.body))

        # Skills
        if rc.skills:
            st += self.section('Core Skills')
            st.append(Paragraph('   ▸   '.join(rc.skills), self.body))

        # Experience
        if rc.experience:
            st += self.section('Experience')
            for exp in rc.experience:
                blk = []
                blk.append(Paragraph(exp.title, self.job_ttl))
                
                sub_parts = [exp.company]
                if exp.location: sub_parts.append(exp.location)
                sub_parts.append(exp.duration)
                blk.append(Paragraph('  |  '.join(sub_parts), self.sub))
                
                for r in (exp.responsibilities or []):
                    blk.append(Paragraph(f'▸ {r}', self.bullet))
                
                blk.append(Spacer(1, 0.06*inch))
                st.append(KeepTogether(blk))

        # Education
        if rc.education:
            st += self.section('Education')
            for edu in rc.education:
                blk = [Paragraph(edu.degree, self.job_ttl)]
                
                sub_parts = [edu.institution, edu.year]
                if edu.gpa: sub_parts.append(f'CGPA: {edu.gpa}')
                blk.append(Paragraph('  |  '.join(sub_parts), self.sub))
                
                blk.append(Spacer(1, 0.04*inch))
                st.append(KeepTogether(blk))

        # Projects
        if rc.projects:
            st += self.section('Projects')
            for p in rc.projects:
                blk = [Paragraph(p.name, self.job_ttl)]
                
                if p.technologies:
                    blk.append(Paragraph(f'Stack: {p.technologies}', self.sub))
                if p.description:
                    blk.append(Paragraph(f'▸ {p.description}', self.bullet))
                if p.impact:
                    blk.append(Paragraph(f'▸ <b>Impact:</b> {p.impact}', self.bullet))
                
                blk.append(Spacer(1, 0.05*inch))
                st.append(KeepTogether(blk))

        # Certifications
        if rc.certifications:
            st += self.section('Certifications')
            for c in rc.certifications:
                if c and c.strip():
                    st.append(Paragraph(f'▸ {c}', self.bullet))
            st.append(Spacer(1, 0.04*inch))

        # Achievements
        if rc.achievements:
            st += self.section('Achievements & Awards')
            for a in rc.achievements:
                if a and a.strip():
                    st.append(Paragraph(f'▸ {a}', self.bullet))

        return st


# ═══════════════════════════════════════════════════════════
#  TEMPLATE 3 — CLASSIC (FIXED SPACING)
# ═══════════════════════════════════════════════════════════
class ClassicTemplate:
    margin = 0.7 * inch

    def __init__(self):
        ss = getSampleStyleSheet()
        def s(name, **kw):
            return ParagraphStyle(name=name, parent=ss['Normal'], **kw)

        self.name     = s('C_Name',  fontSize=22, fontName='Times-Bold',
                          textColor=BLACK, alignment=TA_CENTER, 
                          spaceAfter=1, spaceBefore=0, leading=26)
        
        self.contact  = s('C_Cont',  fontSize=9.5, fontName='Times-Roman',
                          textColor=DGRAY, alignment=TA_CENTER, 
                          spaceAfter=5, spaceBefore=0, leading=12)
        
        self.sec_hdr  = s('C_Sec',   fontSize=11, fontName='Times-Bold',
                          textColor=BLACK, alignment=TA_CENTER, 
                          spaceBefore=9, spaceAfter=1, leading=13)
        
        self.job_ttl  = s('C_Jttl',  fontSize=10.5, fontName='Times-Bold',
                          textColor=BLACK, 
                          spaceAfter=1, spaceBefore=0, leading=13)
        
        self.sub      = s('C_Sub',   fontSize=9.5, fontName='Times-Italic',
                          textColor=DGRAY, 
                          spaceAfter=2, spaceBefore=0, leading=12)
        
        self.body     = s('C_Body',  fontSize=10, fontName='Times-Roman',
                          textColor=BLACK, 
                          leading=13, spaceAfter=4, spaceBefore=0)
        
        self.bullet   = s('C_Bul',   fontSize=9.5, fontName='Times-Roman',
                          textColor=BLACK, leftIndent=16, 
                          spaceAfter=2, spaceBefore=0, leading=12,
                          bulletIndent=0, firstLineIndent=0)

    def divider_full(self):
        return HRFlowable(width="100%", thickness=1, 
                         color=BLACK, spaceAfter=3, spaceBefore=1)

    def section(self, title):
        return [
            Spacer(1, 0.05*inch),
            self.divider_full(),
            Paragraph(title, self.sec_hdr),
            self.divider_full(),
        ]

    def build(self, rc: ResumeContent) -> List:
        st = []

        # Header
        st.append(Paragraph(rc.full_name, self.name))
        cp = _contact_parts(rc)
        if cp: 
            st.append(Paragraph(' | '.join(cp), self.contact))
        st.append(Spacer(1, 0.03*inch))

        # Summary
        if rc.summary:
            st += self.section('PROFESSIONAL SUMMARY')
            st.append(Paragraph(rc.summary, self.body))

        # Skills
        if rc.skills:
            st += self.section('SKILLS')
            st.append(Paragraph(' • '.join(rc.skills), self.body))

        # Experience
        if rc.experience:
            st += self.section('PROFESSIONAL EXPERIENCE')
            for exp in rc.experience:
                blk = []
                blk.append(Paragraph(exp.title, self.job_ttl))
                
                sub_parts = [exp.company, exp.duration]
                if exp.location: sub_parts.append(exp.location)
                blk.append(Paragraph('  |  '.join(sub_parts), self.sub))
                
                for r in (exp.responsibilities or []):
                    blk.append(Paragraph(f'• {r}', self.bullet))
                
                blk.append(Spacer(1, 0.05*inch))
                st.append(KeepTogether(blk))

        # Education
        if rc.education:
            st += self.section('EDUCATION')
            for edu in rc.education:
                blk = [Paragraph(edu.degree, self.job_ttl)]
                
                sub_parts = [edu.institution, edu.year]
                if edu.gpa: sub_parts.append(f'GPA: {edu.gpa}')
                blk.append(Paragraph('  |  '.join(sub_parts), self.sub))
                
                blk.append(Spacer(1, 0.04*inch))
                st.append(KeepTogether(blk))

        # Projects
        if rc.projects:
            st += self.section('PROJECTS')
            for p in rc.projects:
                blk = [Paragraph(p.name, self.job_ttl)]
                
                if p.technologies:
                    blk.append(Paragraph(f'Technologies: {p.technologies}', self.sub))
                if p.description:
                    blk.append(Paragraph(f'• {p.description}', self.bullet))
                if p.impact:
                    blk.append(Paragraph(f'• {p.impact}', self.bullet))
                
                blk.append(Spacer(1, 0.04*inch))
                st.append(KeepTogether(blk))

        # Certifications
        if rc.certifications:
            st += self.section('CERTIFICATIONS')
            for c in rc.certifications:
                if c and c.strip():
                    st.append(Paragraph(f'• {c}', self.bullet))
            st.append(Spacer(1, 0.03*inch))

        # Achievements
        if rc.achievements:
            st += self.section('ACHIEVEMENTS')
            for a in rc.achievements:
                if a and a.strip():
                    st.append(Paragraph(f'• {a}', self.bullet))

        return st


# ── Helper function ────────────────────────────────────────
def _contact_parts(rc: ResumeContent) -> List[str]:
    parts = []
    if rc.contact.phone:    parts.append(rc.contact.phone)
    if rc.contact.email:    parts.append(rc.contact.email)
    if rc.contact.linkedin: parts.append(rc.contact.linkedin)
    if rc.contact.github:   parts.append(rc.contact.github)
    return parts