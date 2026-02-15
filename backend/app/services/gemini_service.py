"""
Gemini AI Service for Resume Generation
Handles all AI-powered content generation using Google's Gemini API
"""
from google import genai
from backend.app.core.config import settings
from backend.app.models.schemas import ResumeContent
from typing import List
from dotenv import load_dotenv
import os
import json
import re

class GeminiService:
    """Service for interacting with Gemini AI"""
    
    def __init__(self):
        """Initialize Gemini API with API key from settings"""
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        print("Listing available models...")
        for m in self.client.models.list():
            print(m.name)


    
    def generate_resume_content(
        self, 
        full_name: str, 
        phone: str, 
        email: str, 
        target_role: str,
        job_description: str = None,
        existing_resume_text: str = None
    ) -> ResumeContent:
        """
        Generate ATS-optimized resume content using Gemini AI
        
        Args:
            full_name: Candidate's full name
            phone: Contact phone number
            email: Contact email
            target_role: Target job position
            job_description: Optional job description for alignment
            existing_resume_text: Optional existing resume content to improve
            
        Returns:
            ResumeContent object with structured resume data
        """
        
        # Construct comprehensive prompt for Gemini
        prompt = self._build_resume_prompt(
            full_name, phone, email, target_role, 
            job_description, existing_resume_text
        )
        
        try:
            # Generate content using Gemini
            response = self.client.models.generate_content(
                            model="gemini-flash-latest",
                            contents=prompt
                        )
            
            # Parse the JSON response
            resume_data = self._parse_gemini_response(response.text)
            
            # Create ResumeContent object
            resume_content = ResumeContent(
                full_name=full_name,
                contact={
                    "phone": phone,
                    "email": email,
                    "linkedin": resume_data.get("linkedin", ""),
                    "github": resume_data.get("github", ""),
                    "portfolio": resume_data.get("portfolio", "")
                },
                summary=resume_data.get("summary", ""),
                skills=resume_data.get("skills", []),
                experience=resume_data.get("experience", []),
                education=resume_data.get("education", []),
                projects=resume_data.get("projects", []),
                certifications=resume_data.get("certifications", []),
                achievements=resume_data.get("achievements", [])
            )
            
            return resume_content
            
        except Exception as e:
            print(f"Error generating resume content: {str(e)}")
            # Return minimal content if generation fails
            return self._create_fallback_content(full_name, phone, email, target_role)
    
    def _build_resume_prompt(
        self, 
        full_name: str, 
        phone: str, 
        email: str, 
        target_role: str,
        job_description: str = None,
        existing_resume_text: str = None
    ) -> str:
        """Build comprehensive prompt for Gemini AI"""
        
        prompt = f"""You are an expert ATS-friendly resume writer and career coach. Generate a professional, ATS-optimized resume for the following candidate.

**Candidate Information:**
- Name: {full_name}
- Phone: {phone}
- Email: {email}
- Target Role: {target_role}

"""
        
        if job_description:
            prompt += f"""**Job Description:**
{job_description}

"""
        
        if existing_resume_text:
            prompt += f"""**Existing Resume Content:**
{existing_resume_text}

"""
        
        prompt += """**Instructions:**
1. Generate a complete, ATS-optimized resume with the following sections:
   - Professional Summary (3-4 impactful sentences)
   - Skills (list 10-15 relevant technical and soft skills)
   - Work Experience (3-5 positions with 4-6 bullet points each using action verbs)
   - Education (degrees with institutions and years)
   - Projects (2-4 relevant projects with descriptions)
   - Certifications (relevant certifications)
   - Achievements (notable accomplishments)

2. Use strong action verbs: Developed, Implemented, Led, Architected, Optimized, Designed, etc.

3. Include quantifiable metrics where possible (percentages, numbers, impact)

4. Align content with the target role and job description (if provided)

5. Extract and incorporate relevant keywords from the job description

6. Use clean, standard formatting suitable for ATS systems

7. Avoid graphics, tables, special characters, or complex formatting

**Output Format:**
Return ONLY a valid JSON object with this exact structure:
{
  "summary": "Professional summary text here",
  "skills": ["Skill 1", "Skill 2", "Skill 3", ...],
  "experience": [
    {
      "title": "Job Title",
      "company": "Company Name",
      "duration": "Jan 2020 - Present",
      "location": "City, State",
      "responsibilities": [
        "Action verb + achievement with metrics",
        "Another accomplishment",
        ...
      ]
    }
  ],
  "education": [
    {
      "degree": "Degree Name",
      "institution": "University Name",
      "year": "2020",
      "gpa": "3.8/4.0"
    }
  ],
  "projects": [
    {
      "name": "Project Name",
      "description": "Brief description",
      "technologies": "Tech stack used",
      "impact": "Measurable impact or outcome"
    }
  ],
  "certifications": ["Certification 1", "Certification 2", ...],
  "achievements": ["Achievement 1", "Achievement 2", ...],
  "linkedin": "LinkedIn URL (optional)",
  "github": "GitHub URL (optional)",
  "portfolio": "Portfolio URL (optional)"
}

Generate professional, impactful content that will pass ATS screening and impress recruiters."""
        
        return prompt
    
    def _parse_gemini_response(self, response_text: str) -> dict:
        """Parse Gemini's JSON response, handling markdown code blocks"""
        try:
            # Remove markdown code blocks if present
            cleaned_text = re.sub(r'```json\s*', '', response_text)
            cleaned_text = re.sub(r'```\s*$', '', cleaned_text)
            cleaned_text = cleaned_text.strip()
            
            # Parse JSON
            data = json.loads(cleaned_text)
            return data
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            print(f"Response text: {response_text[:500]}")
            return {}
    
    def _create_fallback_content(
        self, 
        full_name: str, 
        phone: str, 
        email: str, 
        target_role: str
    ) -> ResumeContent:
        """Create minimal fallback content if AI generation fails"""
        return ResumeContent(
            full_name=full_name,
            contact={
                "phone": phone,
                "email": email,
                "linkedin": "",
                "github": "",
                "portfolio": ""
            },
            summary=f"Motivated professional seeking {target_role} position. Skilled in multiple technologies with proven track record of delivering results.",
            skills=["Communication", "Problem Solving", "Team Collaboration", "Technical Skills", "Project Management"],
            experience=[],
            education=[],
            projects=[],
            certifications=[],
            achievements=[]
        )
    
    def enhance_bullet_points(self, bullet_points: List[str]) -> List[str]:
        """Enhance bullet points with action verbs and impact"""
        if not bullet_points:
            return []
        
        prompt = f"""You are a resume writing expert. Improve these bullet points to be more impactful and ATS-friendly:

{chr(10).join(f'- {point}' for point in bullet_points)}

Requirements:
1. Start each with a strong action verb
2. Include quantifiable metrics where possible
3. Keep them concise (1-2 lines each)
4. Focus on achievements and impact
5. Use industry-standard terminology

Return ONLY a JSON array of improved bullet points:
["Improved point 1", "Improved point 2", ...]"""
        
        try:
            response = self.client.models.generate_content(
                            model="gemini-flash-latest",
                            contents=prompt
                        )
            cleaned = re.sub(r'```json\s*', '', response.text)
            cleaned = re.sub(r'```\s*$', '', cleaned).strip()
            enhanced = json.loads(cleaned)
            return enhanced if isinstance(enhanced, list) else bullet_points
        except:
            return bullet_points