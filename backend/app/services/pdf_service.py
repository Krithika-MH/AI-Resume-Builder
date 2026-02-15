"""
PDF Generation Service using ReportLab
Creates professional, ATS-friendly PDF resumes
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from backend.app.models.schemas import ResumeContent
from io import BytesIO
from typing import List

class PDFGenerationService:
    """Service for generating PDF resumes"""
    
    def __init__(self):
        """Initialize PDF generation service"""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for resume"""
        
        # Title style (Name)
        self.styles.add(ParagraphStyle(
            name='ResumeName',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Contact info style
        self.styles.add(ParagraphStyle(
            name='ContactInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            alignment=TA_CENTER,
            spaceAfter=12
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=colors.HexColor('#2c3e50'),
            borderPadding=2
        ))
        
        # Body text style
        self.styles.add(ParagraphStyle(
            name='ResumeBody',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=6,
            leading=14
        ))
        
        # Bullet point style
        self.styles.add(ParagraphStyle(
            name='BulletPoint',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#1a1a1a'),
            leftIndent=20,
            spaceAfter=4,
            leading=12,
            bulletIndent=10
        ))
        
        # Job title style
        self.styles.add(ParagraphStyle(
            name='JobTitle',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#1a1a1a'),
            fontName='Helvetica-Bold',
            spaceAfter=2
        ))
        
        # Company/Institution style
        self.styles.add(ParagraphStyle(
            name='CompanyName',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#555555'),
            fontName='Helvetica-Oblique',
            spaceAfter=4
        ))
    
    def generate_pdf(self, resume_content: ResumeContent, template: str = "professional") -> BytesIO:
        """
        Generate PDF resume from content
        
        Args:
            resume_content: Structured resume content
            template: Template style to use
            
        Returns:
            BytesIO object containing the PDF
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Build content based on template
        if template == "modern":
            story = self._build_modern_template(resume_content)
        elif template == "classic":
            story = self._build_classic_template(resume_content)
        else:  # professional (default)
            story = self._build_professional_template(resume_content)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def _build_professional_template(self, content: ResumeContent) -> List:
        """Build professional template layout"""
        story = []
        
        # Header - Name
        story.append(Paragraph(content.full_name, self.styles['ResumeName']))
        
        # Contact Information
        contact_parts = []
        if content.contact.get('phone'):
            contact_parts.append(content.contact['phone'])
        if content.contact.get('email'):
            contact_parts.append(content.contact['email'])
        if content.contact.get('linkedin'):
            contact_parts.append(content.contact['linkedin'])
        
        contact_text = " | ".join(contact_parts)
        story.append(Paragraph(contact_text, self.styles['ContactInfo']))
        story.append(Spacer(1, 0.2*inch))
        
        # Professional Summary
        if content.summary:
            story.append(Paragraph("PROFESSIONAL SUMMARY", self.styles['SectionHeader']))
            story.append(Paragraph(content.summary, self.styles['ResumeBody']))
            story.append(Spacer(1, 0.15*inch))
        
        # Skills
        if content.skills:
            story.append(Paragraph("SKILLS", self.styles['SectionHeader']))
            skills_text = " • ".join(content.skills)
            story.append(Paragraph(skills_text, self.styles['ResumeBody']))
            story.append(Spacer(1, 0.15*inch))
        
        # Experience
        if content.experience:
            story.append(Paragraph("PROFESSIONAL EXPERIENCE", self.styles['SectionHeader']))
            for exp in content.experience:
                # Job title and duration
                title_text = f"<b>{exp.get('title', 'Position')}</b>"
                story.append(Paragraph(title_text, self.styles['JobTitle']))
                
                # Company and location
                company_text = f"{exp.get('company', 'Company')} | {exp.get('duration', '')}"
                if exp.get('location'):
                    company_text += f" | {exp['location']}"
                story.append(Paragraph(company_text, self.styles['CompanyName']))
                
                # Responsibilities
                for resp in exp.get('responsibilities', []):
                    bullet_text = f"• {resp}"
                    story.append(Paragraph(bullet_text, self.styles['BulletPoint']))
                
                story.append(Spacer(1, 0.1*inch))
        
        # Education
        if content.education:
            story.append(Paragraph("EDUCATION", self.styles['SectionHeader']))
            for edu in content.education:
                degree_text = f"<b>{edu.get('degree', 'Degree')}</b>"
                story.append(Paragraph(degree_text, self.styles['JobTitle']))
                
                institution_text = f"{edu.get('institution', 'University')} | {edu.get('year', '')}"
                if edu.get('gpa'):
                    institution_text += f" | GPA: {edu['gpa']}"
                story.append(Paragraph(institution_text, self.styles['CompanyName']))
                story.append(Spacer(1, 0.08*inch))
        
        # Projects
        if content.projects:
            story.append(Paragraph("PROJECTS", self.styles['SectionHeader']))
            for proj in content.projects:
                proj_name = f"<b>{proj.get('name', 'Project')}</b>"
                story.append(Paragraph(proj_name, self.styles['JobTitle']))
                
                if proj.get('technologies'):
                    tech_text = f"Technologies: {proj['technologies']}"
                    story.append(Paragraph(tech_text, self.styles['CompanyName']))
                
                if proj.get('description'):
                    story.append(Paragraph(f"• {proj['description']}", self.styles['BulletPoint']))
                
                if proj.get('impact'):
                    story.append(Paragraph(f"• {proj['impact']}", self.styles['BulletPoint']))
                
                story.append(Spacer(1, 0.08*inch))
        
        # Certifications
        if content.certifications:
            story.append(Paragraph("CERTIFICATIONS", self.styles['SectionHeader']))
            for cert in content.certifications:
                story.append(Paragraph(f"• {cert}", self.styles['BulletPoint']))
            story.append(Spacer(1, 0.08*inch))
        
        # Achievements
        if content.achievements:
            story.append(Paragraph("ACHIEVEMENTS", self.styles['SectionHeader']))
            for achievement in content.achievements:
                story.append(Paragraph(f"• {achievement}", self.styles['BulletPoint']))
        
        return story
    
    def _build_modern_template(self, content: ResumeContent) -> List:
        """Build modern template with colored accents"""
        # Similar to professional but with color accents
        return self._build_professional_template(content)
    
    def _build_classic_template(self, content: ResumeContent) -> List:
        """Build classic template with traditional layout"""
        # Similar to professional but more conservative
        return self._build_professional_template(content)