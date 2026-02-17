"""
PDF Generation Service using ReportLab
Creates professional, ATS-friendly PDF resumes
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable, KeepTogether
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
    
    def _setup_custom_styles(self, template="professional"):
        """Setup custom paragraph styles for resume"""
        
        # Reset styles to avoid inheritance pollution between runs
        self.styles = getSampleStyleSheet()

        # Title style (Name)
        if template == "modern":
            self.styles.add(ParagraphStyle(
                name='ResumeName',
                parent=self.styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#007acc'),   # Bright blue
                spaceAfter=4,
                alignment=TA_LEFT,
                fontName='Helvetica-Bold'
            ))
            self.styles.add(ParagraphStyle(
                name='SectionHeader',
                parent=self.styles['Heading2'],
                fontSize=11,
                textColor=colors.HexColor('#007acc'),
                spaceAfter=4,
                spaceBefore=16,
                fontName='Helvetica-Bold',
                letterSpacing=1
            ))
            self.styles.add(ParagraphStyle(
                name='ContactInfo',
                parent=self.styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#333333'),
                alignment=TA_LEFT,
                fontName='Helvetica',
                spaceAfter=12
            ))
            self.styles.add(ParagraphStyle(
                name='ResumeBody',
                parent=self.styles['Normal'],
                fontSize=10.5,
                textColor=colors.HexColor('#1a1a1a'),
                spaceAfter=6,
                leading=15,
                fontName='Helvetica'
            ))
            self.styles.add(ParagraphStyle(
                name='BulletPoint',
                parent=self.styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#1a1a1a'),
                leftIndent=20,
                spaceAfter=4,
                leading=13,
                fontName='Helvetica',
                bulletIndent=10
            ))
            self.styles.add(ParagraphStyle(
                name='JobTitle',
                parent=self.styles['Normal'],
                fontSize=11,
                textColor=colors.HexColor('#1a1a1a'),
                fontName='Helvetica-Bold',
                spaceAfter=2
            ))
            self.styles.add(ParagraphStyle(
                name='CompanyName',
                parent=self.styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#555555'),
                fontName='Helvetica-Oblique',
                spaceAfter=4
            ))

        elif template == "classic":
            self.styles.add(ParagraphStyle(
                name='ResumeName',
                parent=self.styles['Heading1'],
                fontSize=22,
                textColor=colors.black,
                spaceAfter=6,
                alignment=TA_CENTER,
                fontName='Times-Bold'
            ))
            self.styles.add(ParagraphStyle(
                name='ResumeBody',
                parent=self.styles['Normal'],
                fontSize=11,
                fontName='Times-Roman',
                leading=14,
                spaceAfter=6
            ))
            self.styles.add(ParagraphStyle(
                name='SectionHeader',
                parent=self.styles['Heading2'],
                fontSize=12,
                textColor=colors.black,
                fontName='Times-Bold',
                spaceBefore=10,
                spaceAfter=6
            ))
            self.styles.add(ParagraphStyle(
                name='JobTitle',
                parent=self.styles['Normal'],
                fontSize=11,
                fontName='Times-Bold',
                spaceAfter=2
            ))
            self.styles.add(ParagraphStyle(
                name='CompanyName',
                parent=self.styles['Normal'],
                fontSize=10,
                fontName='Times-Italic',
                spaceAfter=4
            ))
            self.styles.add(ParagraphStyle(
                name='BulletPoint',
                parent=self.styles['Normal'],
                fontSize=10,
                fontName='Times-Roman',
                leftIndent=18,
                spaceAfter=4,
                bulletIndent=10
            ))
            self.styles.add(ParagraphStyle(
                name='ContactInfo',
                parent=self.styles['Normal'],
                fontSize=10,
                textColor=colors.black,
                alignment=TA_CENTER,
                fontName='Times-Roman',
                spaceAfter=12
            ))
        else:  # professional
            self.styles.add(ParagraphStyle(
                name='ResumeName',
                parent=self.styles['Heading1'],
                fontSize=20,
                textColor=colors.black,
                spaceAfter=6,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            ))
            self.styles.add(ParagraphStyle(
                name='SectionHeader',
                parent=self.styles['Heading2'],
                fontSize=12,
                textColor=colors.black,
                spaceAfter=6,
                spaceBefore=10,
                fontName='Helvetica-Bold'
            ))
            self.styles.add(ParagraphStyle(
                name='ContactInfo',
                parent=self.styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#333333'),
                alignment=TA_CENTER,
                fontName='Helvetica',
                spaceAfter=12
            ))
            self.styles.add(ParagraphStyle(
                name='ResumeBody',
                parent=self.styles['Normal'],
                fontSize=10,
                textColor=colors.black,
                spaceAfter=6,
                leading=14,
                fontName='Helvetica'
            ))
            self.styles.add(ParagraphStyle(
                name='BulletPoint',
                parent=self.styles['Normal'],
                fontSize=10,
                textColor=colors.black,
                leftIndent=20,
                spaceAfter=4,
                leading=12,
                fontName='Helvetica',
                bulletIndent=10
            ))
            self.styles.add(ParagraphStyle(
                name='JobTitle',
                parent=self.styles['Normal'],
                fontSize=11,
                textColor=colors.black,
                fontName='Helvetica-Bold',
                spaceAfter=2
            ))
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
        # Reinitialize styles per template
        self._setup_custom_styles(template)
        
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
        if content.contact.phone:
            contact_parts.append(content.contact.phone)
        if content.contact.email:
            contact_parts.append(content.contact.email)
        if content.contact.linkedin:
            contact_parts.append(content.contact.linkedin)
        
        contact_text = " | ".join(contact_parts)
        story.append(Paragraph(contact_text, self.styles['ContactInfo']))
        story.append(Spacer(1, 0.2*inch))
        
        # Professional Summary
        if content.summary:
            story.append(Paragraph("PROFESSIONAL SUMMARY", self.styles['SectionHeader']))
            story.append(Paragraph(content.summary, self.styles['ResumeBody']))
            story.append(Spacer(1, 0.15*inch))
        
        # Skills - Comma separated for ATS
        if content.skills:
            story.append(Paragraph("SKILLS", self.styles['SectionHeader']))
            skills_text = ", ".join(content.skills)
            story.append(Paragraph(skills_text, self.styles['ResumeBody']))
            story.append(Spacer(1, 0.15*inch))
        
        # Experience
        if content.experience:
            story.append(Paragraph("PROFESSIONAL EXPERIENCE", self.styles['SectionHeader']))
            for exp in content.experience:
                block = []
                # Job title and duration
                title_text = f"<b>{exp.title}</b>"
                block.append(Paragraph(title_text, self.styles['JobTitle']))
                
                # Company and location
                company_text = f"{exp.company} | {exp.duration}"
                if exp.location:
                    company_text += f" | {exp.location}"
                block.append(Paragraph(company_text, self.styles['CompanyName']))
                
                # Responsibilities - ATS optimized bullets
                for resp in exp.responsibilities:
                    block.append(Paragraph(resp, self.styles['BulletPoint'], bulletText="•"))
                
                block.append(Spacer(1, 0.1*inch))
                story.append(KeepTogether(block))
        
        # Education
        if content.education:
            story.append(Paragraph("EDUCATION", self.styles['SectionHeader']))
            for edu in content.education:
                degree_text = f"<b>{edu.degree}</b>"
                story.append(Paragraph(degree_text, self.styles['JobTitle']))
                
                institution_text = f"{edu.institution} | {edu.year}"
                if edu.gpa:
                    institution_text += f" | GPA: {edu.gpa}"
                story.append(Paragraph(institution_text, self.styles['CompanyName']))
                story.append(Spacer(1, 0.08*inch))
        
        # Projects
        if content.projects:
            story.append(Paragraph("PROJECTS", self.styles['SectionHeader']))
            for proj in content.projects:
                proj_name = f"<b>{proj.name}</b>"
                story.append(Paragraph(proj_name, self.styles['JobTitle']))
                
                if proj.technologies:
                    tech_text = f"Technologies: {proj.technologies}"
                    story.append(Paragraph(tech_text, self.styles['CompanyName']))
                
                if proj.description:
                    story.append(Paragraph(proj.description, self.styles['BulletPoint'], bulletText="•"))
                
                if proj.impact:
                    story.append(Paragraph(proj.impact, self.styles['BulletPoint'], bulletText="•"))
                
                story.append(Spacer(1, 0.08*inch))
        
        # Certifications
        if content.certifications:
            story.append(Paragraph("CERTIFICATIONS", self.styles['SectionHeader']))
            for cert in content.certifications:
                story.append(Paragraph(cert, self.styles['BulletPoint'], bulletText="•"))
            story.append(Spacer(1, 0.08*inch))
        
        # Achievements
        if content.achievements:
            story.append(Paragraph("ACHIEVEMENTS", self.styles['SectionHeader']))
            for achievement in content.achievements:
                story.append(Paragraph(achievement, self.styles['BulletPoint'], bulletText="•"))
        
        return story
    
    def _build_modern_template(self, content: ResumeContent) -> List:
        """Build modern template with colored accents"""
        story = []
        
        # Header - Name (Left aligned, bigger, colored)
        story.append(Paragraph(content.full_name, self.styles['ResumeName']))
        
        # Thin accent line
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#007acc")))
        story.append(Spacer(1, 0.2*inch))
        
        # Contact Information
        contact_parts = []
        if content.contact.phone:
            contact_parts.append(content.contact.phone)
        if content.contact.email:
            contact_parts.append(content.contact.email)
        if content.contact.linkedin:
            contact_parts.append(content.contact.linkedin)
        
        contact_text = " | ".join(contact_parts)
        story.append(Paragraph(contact_text, self.styles['ContactInfo']))
        story.append(Spacer(1, 0.25*inch))
        
        # Professional Summary
        if content.summary:
            story.append(Paragraph("PROFESSIONAL SUMMARY", self.styles['SectionHeader']))
            story.append(Paragraph(content.summary, self.styles['ResumeBody']))
            story.append(Spacer(1, 0.2*inch))
        
        # Skills - Comma separated for ATS
        if content.skills:
            story.append(Paragraph("SKILLS", self.styles['SectionHeader']))
            skills_text = ", ".join(content.skills)
            story.append(Paragraph(skills_text, self.styles['ResumeBody']))
            story.append(Spacer(1, 0.2*inch))
        
        # Experience
        if content.experience:
            story.append(Paragraph("PROFESSIONAL EXPERIENCE", self.styles['SectionHeader']))
            for exp in content.experience:
                block = []
                # Job title and duration
                title_text = f"<b>{exp.title}</b>"
                block.append(Paragraph(title_text, self.styles['JobTitle']))
                
                # Company and location
                company_text = f"{exp.company} | {exp.duration}"
                if exp.location:
                    company_text += f" | {exp.location}"
                block.append(Paragraph(company_text, self.styles['CompanyName']))
                
                # Responsibilities - ATS optimized bullets
                for resp in exp.responsibilities:
                    block.append(Paragraph(resp, self.styles['BulletPoint'], bulletText="•"))
                
                block.append(Spacer(1, 0.15*inch))
                story.append(KeepTogether(block))
        
        # Education
        if content.education:
            story.append(Paragraph("EDUCATION", self.styles['SectionHeader']))
            for edu in content.education:
                degree_text = f"<b>{edu.degree}</b>"
                story.append(Paragraph(degree_text, self.styles['JobTitle']))
                
                institution_text = f"{edu.institution} | {edu.year}"
                if edu.gpa:
                    institution_text += f" | GPA: {edu.gpa}"
                story.append(Paragraph(institution_text, self.styles['CompanyName']))
                story.append(Spacer(1, 0.1*inch))
        
        # Projects
        if content.projects:
            story.append(Paragraph("PROJECTS", self.styles['SectionHeader']))
            for proj in content.projects:
                proj_name = f"<b>{proj.name}</b>"
                story.append(Paragraph(proj_name, self.styles['JobTitle']))
                
                if proj.technologies:
                    tech_text = f"Technologies: {proj.technologies}"
                    story.append(Paragraph(tech_text, self.styles['CompanyName']))
                
                if proj.description:
                    story.append(Paragraph(proj.description, self.styles['BulletPoint'], bulletText="•"))
                
                if proj.impact:
                    story.append(Paragraph(proj.impact, self.styles['BulletPoint'], bulletText="•"))
                
                story.append(Spacer(1, 0.1*inch))
        
        # Certifications
        if content.certifications:
            story.append(Paragraph("CERTIFICATIONS", self.styles['SectionHeader']))
            for cert in content.certifications:
                story.append(Paragraph(cert, self.styles['BulletPoint'], bulletText="•"))
            story.append(Spacer(1, 0.1*inch))
        
        # Achievements
        if content.achievements:
            story.append(Paragraph("ACHIEVEMENTS", self.styles['SectionHeader']))
            for achievement in content.achievements:
                story.append(Paragraph(achievement, self.styles['BulletPoint'], bulletText="•"))
        
        return story
    
    def _build_classic_template(self, content: ResumeContent) -> List:
        """Build classic template with traditional layout"""
        story = []
        
        # Header - Name (Centered, Times font)
        story.append(Paragraph(content.full_name, self.styles['ResumeName']))
        
        # Contact Information
        contact_parts = []
        if content.contact.phone:
            contact_parts.append(content.contact.phone)
        if content.contact.email:
            contact_parts.append(content.contact.email)
        if content.contact.linkedin:
            contact_parts.append(content.contact.linkedin)
        
        contact_text = " | ".join(contact_parts)
        story.append(Paragraph(contact_text, self.styles['ContactInfo']))
        story.append(Spacer(1, 0.2*inch))
        
        # Professional Summary
        if content.summary:
            story.append(Paragraph("PROFESSIONAL SUMMARY", self.styles['SectionHeader']))
            story.append(Paragraph(content.summary, self.styles['ResumeBody']))
            story.append(Spacer(1, 0.15*inch))
        
        # Skills - Comma separated for ATS
        if content.skills:
            story.append(Paragraph("SKILLS", self.styles['SectionHeader']))
            skills_text = ", ".join(content.skills)
            story.append(Paragraph(skills_text, self.styles['ResumeBody']))
            story.append(Spacer(1, 0.15*inch))
        
        # Experience
        if content.experience:
            story.append(Paragraph("PROFESSIONAL EXPERIENCE", self.styles['SectionHeader']))
            for exp in content.experience:
                block = []
                # Job title and duration
                title_text = f"<b>{exp.title}</b>"
                block.append(Paragraph(title_text, self.styles['JobTitle']))
                
                # Company and location
                company_text = f"{exp.company} | {exp.duration}"
                if exp.location:
                    company_text += f" | {exp.location}"
                block.append(Paragraph(company_text, self.styles['CompanyName']))
                
                # Responsibilities - ATS optimized bullets
                for resp in exp.responsibilities:
                    block.append(Paragraph(resp, self.styles['BulletPoint'], bulletText="•"))
                
                block.append(Spacer(1, 0.1*inch))
                story.append(KeepTogether(block))
        
        # Education
        if content.education:
            story.append(Paragraph("EDUCATION", self.styles['SectionHeader']))
            for edu in content.education:
                degree_text = f"<b>{edu.degree}</b>"
                story.append(Paragraph(degree_text, self.styles['JobTitle']))
                
                institution_text = f"{edu.institution} | {edu.year}"
                if edu.gpa:
                    institution_text += f" | GPA: {edu.gpa}"
                story.append(Paragraph(institution_text, self.styles['CompanyName']))
                story.append(Spacer(1, 0.08*inch))
        
        # Projects
        if content.projects:
            story.append(Paragraph("PROJECTS", self.styles['SectionHeader']))
            for proj in content.projects:
                proj_name = f"<b>{proj.name}</b>"
                story.append(Paragraph(proj_name, self.styles['JobTitle']))
                
                if proj.technologies:
                    tech_text = f"Technologies: {proj.technologies}"
                    story.append(Paragraph(tech_text, self.styles['CompanyName']))
                
                if proj.description:
                    story.append(Paragraph(proj.description, self.styles['BulletPoint'], bulletText="•"))
                
                if proj.impact:
                    story.append(Paragraph(proj.impact, self.styles['BulletPoint'], bulletText="•"))
                
                story.append(Spacer(1, 0.08*inch))
        
        # Certifications
        if content.certifications:
            story.append(Paragraph("CERTIFICATIONS", self.styles['SectionHeader']))
            for cert in content.certifications:
                story.append(Paragraph(cert, self.styles['BulletPoint'], bulletText="•"))
            story.append(Spacer(1, 0.08*inch))
        
        # Achievements
        if content.achievements:
            story.append(Paragraph("ACHIEVEMENTS", self.styles['SectionHeader']))
            for achievement in content.achievements:
                story.append(Paragraph(achievement, self.styles['BulletPoint'], bulletText="•"))
        
        return story