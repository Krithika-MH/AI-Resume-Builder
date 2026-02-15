"""
DOCX Generation Service using python-docx
Creates editable, ATS-friendly Word documents
"""
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from backend.app.models.schemas import ResumeContent
from io import BytesIO

class DOCXGenerationService:
    """Service for generating DOCX resumes"""
    
    def generate_docx(self, resume_content: ResumeContent, template: str = "professional") -> BytesIO:
        """
        Generate DOCX resume from content
        
        Args:
            resume_content: Structured resume content
            template: Template style to use
            
        Returns:
            BytesIO object containing the DOCX file
        """
        doc = Document()
        
        # Set document margins
        sections = doc.sections
        for section in sections:
            section.top_margin = Inches(0.75)
            section.bottom_margin = Inches(0.75)
            section.left_margin = Inches(0.75)
            section.right_margin = Inches(0.75)
        
        # Build content based on template
        if template == "modern":
            self._build_modern_template(doc, resume_content)
        elif template == "classic":
            self._build_classic_template(doc, resume_content)
        else:  # professional (default)
            self._build_professional_template(doc, resume_content)
        
        # Save to BytesIO
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer
    
    def _build_professional_template(self, doc: Document, content: ResumeContent):
        """Build professional template layout"""
        
        # Header - Name (Centered, Bold, Large)
        name_para = doc.add_paragraph()
        name_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        name_run = name_para.add_run(content.full_name)
        name_run.font.size = Pt(20)
        name_run.font.bold = True
        name_run.font.color.rgb = RGBColor(26, 26, 26)
        
        # Contact Information (Centered)
        contact_parts = []
        if content.contact.get('phone'):
            contact_parts.append(content.contact['phone'])
        if content.contact.get('email'):
            contact_parts.append(content.contact['email'])
        if content.contact.get('linkedin'):
            contact_parts.append(content.contact['linkedin'])
        
        if contact_parts:
            contact_para = doc.add_paragraph()
            contact_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            contact_run = contact_para.add_run(" | ".join(contact_parts))
            contact_run.font.size = Pt(10)
            contact_run.font.color.rgb = RGBColor(51, 51, 51)
        
        # Add spacing
        doc.add_paragraph()
        
        # Professional Summary
        if content.summary:
            self._add_section_header(doc, "PROFESSIONAL SUMMARY")
            summary_para = doc.add_paragraph(content.summary)
            summary_para.paragraph_format.space_after = Pt(12)
            self._format_body_text(summary_para)
        
        # Skills
        if content.skills:
            self._add_section_header(doc, "SKILLS")
            skills_text = " • ".join(content.skills)
            skills_para = doc.add_paragraph(skills_text)
            skills_para.paragraph_format.space_after = Pt(12)
            self._format_body_text(skills_para)
        
        # Professional Experience
        if content.experience:
            self._add_section_header(doc, "PROFESSIONAL EXPERIENCE")
            
            for exp in content.experience:
                # Job Title (Bold)
                title_para = doc.add_paragraph()
                title_run = title_para.add_run(exp.get('title', 'Position'))
                title_run.font.size = Pt(11)
                title_run.font.bold = True
                title_run.font.color.rgb = RGBColor(26, 26, 26)
                title_para.paragraph_format.space_after = Pt(2)
                
                # Company, Duration, Location (Italic)
                company_para = doc.add_paragraph()
                company_text = f"{exp.get('company', 'Company')} | {exp.get('duration', '')}"
                if exp.get('location'):
                    company_text += f" | {exp['location']}"
                company_run = company_para.add_run(company_text)
                company_run.font.size = Pt(10)
                company_run.font.italic = True
                company_run.font.color.rgb = RGBColor(85, 85, 85)
                company_para.paragraph_format.space_after = Pt(4)
                
                # Responsibilities (Bulleted)
                for resp in exp.get('responsibilities', []):
                    bullet_para = doc.add_paragraph(resp, style='List Bullet')
                    bullet_para.paragraph_format.left_indent = Inches(0.25)
                    bullet_para.paragraph_format.space_after = Pt(3)
                    self._format_body_text(bullet_para, size=9)
                
                # Add spacing between jobs
                doc.add_paragraph()
        
        # Education
        if content.education:
            self._add_section_header(doc, "EDUCATION")
            
            for edu in content.education:
                # Degree (Bold)
                degree_para = doc.add_paragraph()
                degree_run = degree_para.add_run(edu.get('degree', 'Degree'))
                degree_run.font.size = Pt(11)
                degree_run.font.bold = True
                degree_run.font.color.rgb = RGBColor(26, 26, 26)
                degree_para.paragraph_format.space_after = Pt(2)
                
                # Institution and Year
                inst_para = doc.add_paragraph()
                inst_text = f"{edu.get('institution', 'University')} | {edu.get('year', '')}"
                if edu.get('gpa'):
                    inst_text += f" | GPA: {edu['gpa']}"
                inst_run = inst_para.add_run(inst_text)
                inst_run.font.size = Pt(10)
                inst_run.font.italic = True
                inst_run.font.color.rgb = RGBColor(85, 85, 85)
                inst_para.paragraph_format.space_after = Pt(8)
        
        # Projects
        if content.projects:
            self._add_section_header(doc, "PROJECTS")
            
            for proj in content.projects:
                # Project Name (Bold)
                proj_para = doc.add_paragraph()
                proj_run = proj_para.add_run(proj.get('name', 'Project'))
                proj_run.font.size = Pt(11)
                proj_run.font.bold = True
                proj_run.font.color.rgb = RGBColor(26, 26, 26)
                proj_para.paragraph_format.space_after = Pt(2)
                
                # Technologies
                if proj.get('technologies'):
                    tech_para = doc.add_paragraph()
                    tech_run = tech_para.add_run(f"Technologies: {proj['technologies']}")
                    tech_run.font.size = Pt(10)
                    tech_run.font.italic = True
                    tech_run.font.color.rgb = RGBColor(85, 85, 85)
                    tech_para.paragraph_format.space_after = Pt(4)
                
                # Description and Impact (Bulleted)
                if proj.get('description'):
                    desc_para = doc.add_paragraph(proj['description'], style='List Bullet')
                    desc_para.paragraph_format.left_indent = Inches(0.25)
                    self._format_body_text(desc_para, size=9)
                
                if proj.get('impact'):
                    impact_para = doc.add_paragraph(proj['impact'], style='List Bullet')
                    impact_para.paragraph_format.left_indent = Inches(0.25)
                    self._format_body_text(impact_para, size=9)
                
                doc.add_paragraph()
        
        # Certifications
        if content.certifications:
            self._add_section_header(doc, "CERTIFICATIONS")
            for cert in content.certifications:
                cert_para = doc.add_paragraph(cert, style='List Bullet')
                cert_para.paragraph_format.left_indent = Inches(0.25)
                self._format_body_text(cert_para, size=9)
        
        # Achievements
        if content.achievements:
            self._add_section_header(doc, "ACHIEVEMENTS")
            for achievement in content.achievements:
                ach_para = doc.add_paragraph(achievement, style='List Bullet')
                ach_para.paragraph_format.left_indent = Inches(0.25)
                self._format_body_text(ach_para, size=9)
    
    def _add_section_header(self, doc: Document, header_text: str):
        """Add formatted section header"""
        header_para = doc.add_paragraph()
        header_run = header_para.add_run(header_text)
        header_run.font.size = Pt(14)
        header_run.font.bold = True
        header_run.font.color.rgb = RGBColor(44, 62, 80)
        
        # Add bottom border to section header
        header_para.paragraph_format.space_after = Pt(8)
        header_para.paragraph_format.space_before = Pt(12)
    
    def _format_body_text(self, paragraph, size: int = 10):
        """Format paragraph as body text"""
        for run in paragraph.runs:
            run.font.size = Pt(size)
            run.font.name = 'Calibri'
            run.font.color.rgb = RGBColor(26, 26, 26)
    
    def _build_modern_template(self, doc: Document, content: ResumeContent):
        """Build modern template with color accents"""
        # Similar to professional but with more color
        self._build_professional_template(doc, content)
    
    def _build_classic_template(self, doc: Document, content: ResumeContent):
        """Build classic template with traditional layout"""
        # Similar to professional but more conservative
        self._build_professional_template(doc, content)