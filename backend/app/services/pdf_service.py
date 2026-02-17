"""
PDF Generation Service – 3 visually distinct templates.
Professional: Helvetica, centered header, thin dividers, black/grey.
Modern (FAANG): Left-aligned, navy+green accent, impact-focused layout.
Classic: Times New Roman, centered, full-width ruled dividers, serif.
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    KeepTogether, Table, TableStyle
)
from reportlab.lib import colors
from backend.app.models.schemas import ResumeContent
from io import BytesIO
from typing import List


# ── Colour palette (matches logo) ─────────────────────────
NAVY   = colors.HexColor('#1E3A4C')
GREEN  = colors.HexColor('#2E7D52')
GREEN2 = colors.HexColor('#3D9E68')
GOLD   = colors.HexColor('#E8B84B')
BLACK  = colors.HexColor('#111111')
DGRAY  = colors.HexColor('#444444')
LGRAY  = colors.HexColor('#888888')
PALE   = colors.HexColor('#F0FDF4')


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
            topMargin=builder.margin,   bottomMargin=builder.margin,
        )
        doc.build(builder.build(resume_content))
        buf.seek(0)
        return buf


# ═══════════════════════════════════════════════════════════
#  TEMPLATE 1 — PROFESSIONAL
#  Helvetica, centered header, thin HR dividers, black+grey
# ═══════════════════════════════════════════════════════════
class ProfessionalTemplate:
    margin = 0.7 * inch

    def __init__(self):
        ss = getSampleStyleSheet()
        def s(name, **kw):
            return ParagraphStyle(name=name, parent=ss['Normal'], **kw)

        self.name     = s('P_Name',  fontSize=22, fontName='Helvetica-Bold',
                          textColor=BLACK, alignment=TA_CENTER, spaceAfter=3)
        self.contact  = s('P_Cont',  fontSize=9.5, fontName='Helvetica',
                          textColor=DGRAY, alignment=TA_CENTER, spaceAfter=8)
        self.sec_hdr  = s('P_Sec',   fontSize=10.5, fontName='Helvetica-Bold',
                          textColor=BLACK, spaceBefore=10, spaceAfter=4, letterSpacing=1.2)
        self.job_ttl  = s('P_Jttl',  fontSize=10.5, fontName='Helvetica-Bold',
                          textColor=BLACK, spaceAfter=1)
        self.sub      = s('P_Sub',   fontSize=9.5, fontName='Helvetica-Oblique',
                          textColor=LGRAY, spaceAfter=3)
        self.body     = s('P_Body',  fontSize=10, fontName='Helvetica',
                          textColor=BLACK, leading=14, spaceAfter=5)
        self.bullet   = s('P_Bul',   fontSize=9.5, fontName='Helvetica',
                          textColor=BLACK, leftIndent=14, spaceAfter=3, leading=13)

    def divider(self):
        return HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CCCCCC'), spaceAfter=6)

    def section(self, title):
        return [
            Paragraph(title.upper(), self.sec_hdr),
            self.divider(),
        ]

    def build(self, rc: ResumeContent) -> List:
        st = []

        st.append(Paragraph(rc.full_name, self.name))
        cp = _contact_parts(rc)
        if cp: st.append(Paragraph(' | '.join(cp), self.contact))
        st.append(Spacer(1, 0.15*inch))

        if rc.summary:
            st += self.section('Professional Summary')
            st.append(Paragraph(rc.summary, self.body))
            st.append(Spacer(1, 0.08*inch))

        if rc.skills:
            st += self.section('Skills')
            st.append(Paragraph(', '.join(rc.skills), self.body))
            st.append(Spacer(1, 0.08*inch))

        if rc.experience:
            st += self.section('Professional Experience')
            for exp in rc.experience:
                blk = []
                blk.append(Paragraph(f'<b>{exp.title}</b>', self.job_ttl))
                sub = f'{exp.company} | {exp.duration}'
                if exp.location: sub += f' | {exp.location}'
                blk.append(Paragraph(sub, self.sub))
                for r in (exp.responsibilities or []):
                    blk.append(Paragraph(r, self.bullet, bulletText='•'))
                blk.append(Spacer(1, 0.08*inch))
                st.append(KeepTogether(blk))

        if rc.education:
            st += self.section('Education')
            for edu in rc.education:
                blk = [Paragraph(f'<b>{edu.degree}</b>', self.job_ttl)]
                sub = f'{edu.institution} | {edu.year}'
                if edu.gpa: sub += f' | GPA: {edu.gpa}'
                blk.append(Paragraph(sub, self.sub))
                blk.append(Spacer(1, 0.06*inch))
                st.append(KeepTogether(blk))

        if rc.projects:
            st += self.section('Projects')
            for p in rc.projects:
                blk = [Paragraph(f'<b>{p.name}</b>', self.job_ttl)]
                if p.technologies:
                    blk.append(Paragraph(f'Technologies: {p.technologies}', self.sub))
                if p.description:
                    blk.append(Paragraph(p.description, self.bullet, bulletText='•'))
                if p.impact:
                    blk.append(Paragraph(p.impact, self.bullet, bulletText='•'))
                blk.append(Spacer(1, 0.06*inch))
                st.append(KeepTogether(blk))

        if rc.certifications:
            st += self.section('Certifications')
            for c in rc.certifications:
                if c and c.strip():
                    st.append(Paragraph(c, self.bullet, bulletText='•'))
            st.append(Spacer(1, 0.06*inch))

        if rc.achievements:
            st += self.section('Achievements')
            for a in rc.achievements:
                if a and a.strip():
                    st.append(Paragraph(a, self.bullet, bulletText='•'))

        return st


# ═══════════════════════════════════════════════════════════
#  TEMPLATE 2 — MODERN (FAANG)
#  Navy name, green accent line, left-aligned, metric-heavy
# ═══════════════════════════════════════════════════════════
class ModernTemplate:
    margin = 0.65 * inch

    def __init__(self):
        ss = getSampleStyleSheet()
        def s(name, **kw):
            return ParagraphStyle(name=name, parent=ss['Normal'], **kw)

        self.name     = s('M_Name',  fontSize=26, fontName='Helvetica-Bold',
                          textColor=NAVY, alignment=TA_LEFT, spaceAfter=2)
        self.role_tag = s('M_Role',  fontSize=12, fontName='Helvetica',
                          textColor=GREEN, alignment=TA_LEFT, spaceAfter=6)
        self.contact  = s('M_Cont',  fontSize=9.5, fontName='Helvetica',
                          textColor=DGRAY, alignment=TA_LEFT, spaceAfter=10)
        self.sec_hdr  = s('M_Sec',   fontSize=11, fontName='Helvetica-Bold',
                          textColor=GREEN, spaceBefore=14, spaceAfter=3, letterSpacing=0.8)
        self.job_ttl  = s('M_Jttl',  fontSize=11, fontName='Helvetica-Bold',
                          textColor=NAVY, spaceAfter=1)
        self.sub      = s('M_Sub',   fontSize=9.5, fontName='Helvetica',
                          textColor=LGRAY, spaceAfter=3)
        self.body     = s('M_Body',  fontSize=10, fontName='Helvetica',
                          textColor=BLACK, leading=14, spaceAfter=5)
        self.bullet   = s('M_Bul',   fontSize=9.5, fontName='Helvetica',
                          textColor=BLACK, leftIndent=14, spaceAfter=3, leading=13)

    def green_line(self):
        return HRFlowable(width="100%", thickness=2, color=GREEN, spaceAfter=8, spaceBefore=0)

    def section(self, title):
        return [
            Paragraph(title.upper(), self.sec_hdr),
            HRFlowable(width="100%", thickness=1, color=colors.HexColor('#D1E8DB'), spaceAfter=5),
        ]

    def build(self, rc: ResumeContent) -> List:
        st = []

        st.append(Paragraph(rc.full_name, self.name))
        st.append(self.green_line())

        cp = _contact_parts(rc)
        if cp: st.append(Paragraph('  ·  '.join(cp), self.contact))
        st.append(Spacer(1, 0.1*inch))

        if rc.summary:
            st += self.section('Profile')
            st.append(Paragraph(rc.summary, self.body))

        if rc.skills:
            st += self.section('Core Skills')
            # Group skills into rows of 4 for a modern pill layout
            skill_text = '   ▸   '.join(rc.skills)
            st.append(Paragraph(skill_text, self.body))
            st.append(Spacer(1, 0.05*inch))

        if rc.experience:
            st += self.section('Experience')
            for exp in rc.experience:
                blk = []
                # Two-column: title | duration
                title_run = f'<b>{exp.title}</b>'
                blk.append(Paragraph(title_run, self.job_ttl))
                sub = f'{exp.company}'
                if exp.location: sub += f', {exp.location}'
                sub += f'  |  {exp.duration}'
                blk.append(Paragraph(sub, self.sub))
                for r in (exp.responsibilities or []):
                    blk.append(Paragraph(r, self.bullet, bulletText='▸'))
                blk.append(Spacer(1, 0.1*inch))
                st.append(KeepTogether(blk))

        if rc.education:
            st += self.section('Education')
            for edu in rc.education:
                blk = [Paragraph(f'<b>{edu.degree}</b>', self.job_ttl)]
                sub = f'{edu.institution}  |  {edu.year}'
                if edu.gpa: sub += f'  |  CGPA: {edu.gpa}'
                blk.append(Paragraph(sub, self.sub))
                blk.append(Spacer(1, 0.06*inch))
                st.append(KeepTogether(blk))

        if rc.projects:
            st += self.section('Projects')
            for p in rc.projects:
                blk = [Paragraph(f'<b>{p.name}</b>', self.job_ttl)]
                if p.technologies:
                    blk.append(Paragraph(f'Stack: {p.technologies}', self.sub))
                if p.description:
                    blk.append(Paragraph(p.description, self.bullet, bulletText='▸'))
                if p.impact:
                    blk.append(Paragraph(f'<b>Impact:</b> {p.impact}', self.bullet, bulletText='▸'))
                blk.append(Spacer(1, 0.07*inch))
                st.append(KeepTogether(blk))

        if rc.certifications:
            st += self.section('Certifications')
            for c in rc.certifications:
                if c and c.strip():
                    st.append(Paragraph(c, self.bullet, bulletText='▸'))
            st.append(Spacer(1, 0.06*inch))

        if rc.achievements:
            st += self.section('Achievements & Awards')
            for a in rc.achievements:
                if a and a.strip():
                    st.append(Paragraph(a, self.bullet, bulletText='▸'))

        return st


# ═══════════════════════════════════════════════════════════
#  TEMPLATE 3 — CLASSIC
#  Times New Roman, centered name, full-width ruled dividers
# ═══════════════════════════════════════════════════════════
class ClassicTemplate:
    margin = 0.8 * inch

    def __init__(self):
        ss = getSampleStyleSheet()
        def s(name, **kw):
            return ParagraphStyle(name=name, parent=ss['Normal'], **kw)

        self.name     = s('C_Name',  fontSize=24, fontName='Times-Bold',
                          textColor=BLACK, alignment=TA_CENTER, spaceAfter=2)
        self.contact  = s('C_Cont',  fontSize=10, fontName='Times-Roman',
                          textColor=DGRAY, alignment=TA_CENTER, spaceAfter=6)
        self.sec_hdr  = s('C_Sec',   fontSize=12, fontName='Times-Bold',
                          textColor=BLACK, spaceBefore=12, spaceAfter=2,
                          alignment=TA_CENTER, letterSpacing=2)
        self.job_ttl  = s('C_Jttl',  fontSize=11, fontName='Times-Bold',
                          textColor=BLACK, spaceAfter=1)
        self.sub      = s('C_Sub',   fontSize=10, fontName='Times-Italic',
                          textColor=DGRAY, spaceAfter=4)
        self.body     = s('C_Body',  fontSize=10.5, fontName='Times-Roman',
                          textColor=BLACK, leading=15, spaceAfter=5)
        self.bullet   = s('C_Bul',   fontSize=10, fontName='Times-Roman',
                          textColor=BLACK, leftIndent=18, spaceAfter=4, leading=14)

    def divider_full(self):
        return HRFlowable(width="100%", thickness=1, color=BLACK, spaceAfter=6, spaceBefore=2)

    def divider_thin(self):
        return HRFlowable(width="100%", thickness=0.4, color=LGRAY, spaceAfter=5)

    def section(self, title):
        return [
            self.divider_full(),
            Paragraph(title, self.sec_hdr),
            self.divider_full(),
        ]

    def build(self, rc: ResumeContent) -> List:
        st = []

        st.append(Paragraph(rc.full_name, self.name))
        cp = _contact_parts(rc)
        if cp: st.append(Paragraph(' | '.join(cp), self.contact))
        st.append(Spacer(1, 0.05*inch))

        if rc.summary:
            st += self.section('PROFESSIONAL SUMMARY')
            st.append(Paragraph(rc.summary, self.body))
            st.append(Spacer(1, 0.05*inch))

        if rc.skills:
            st += self.section('SKILLS')
            st.append(Paragraph(' • '.join(rc.skills), self.body))
            st.append(Spacer(1, 0.05*inch))

        if rc.experience:
            st += self.section('PROFESSIONAL EXPERIENCE')
            for exp in rc.experience:
                blk = []
                blk.append(Paragraph(f'<b>{exp.title}</b>', self.job_ttl))
                sub = f'{exp.company}  |  {exp.duration}'
                if exp.location: sub += f'  |  {exp.location}'
                blk.append(Paragraph(sub, self.sub))
                for r in (exp.responsibilities or []):
                    blk.append(Paragraph(r, self.bullet, bulletText='•'))
                blk.append(Spacer(1, 0.08*inch))
                st.append(KeepTogether(blk))

        if rc.education:
            st += self.section('EDUCATION')
            for edu in rc.education:
                blk = [Paragraph(f'<b>{edu.degree}</b>', self.job_ttl)]
                sub = f'{edu.institution}  |  {edu.year}'
                if edu.gpa: sub += f'  |  GPA: {edu.gpa}'
                blk.append(Paragraph(sub, self.sub))
                blk.append(Spacer(1, 0.06*inch))
                st.append(KeepTogether(blk))

        if rc.projects:
            st += self.section('PROJECTS')
            for p in rc.projects:
                blk = [Paragraph(f'<b>{p.name}</b>', self.job_ttl)]
                if p.technologies:
                    blk.append(Paragraph(f'Technologies: {p.technologies}', self.sub))
                if p.description:
                    blk.append(Paragraph(p.description, self.bullet, bulletText='•'))
                if p.impact:
                    blk.append(Paragraph(p.impact, self.bullet, bulletText='•'))
                blk.append(Spacer(1, 0.06*inch))
                st.append(KeepTogether(blk))

        if rc.certifications:
            st += self.section('CERTIFICATIONS')
            for c in rc.certifications:
                if c and c.strip():
                    st.append(Paragraph(c, self.bullet, bulletText='•'))
            st.append(Spacer(1, 0.05*inch))

        if rc.achievements:
            st += self.section('ACHIEVEMENTS')
            for a in rc.achievements:
                if a and a.strip():
                    st.append(Paragraph(a, self.bullet, bulletText='•'))

        return st


# ── Shared helper ──────────────────────────────────────────
def _contact_parts(rc: ResumeContent) -> List[str]:
    parts = []
    if rc.contact.phone:    parts.append(rc.contact.phone)
    if rc.contact.email:    parts.append(rc.contact.email)
    if rc.contact.linkedin: parts.append(rc.contact.linkedin)
    if rc.contact.github:   parts.append(rc.contact.github)
    return parts