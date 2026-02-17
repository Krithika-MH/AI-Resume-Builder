"""
ATS Scoring Service
Implements industry-standard ATS scoring algorithms
"""
from backend.app.models.schemas import ATSScore, ResumeContent
from typing import List, Dict, Set
import re
from collections import Counter


class ATSScoringService:
    """Service for calculating ATS compatibility scores"""
    
    # Industry-standard action verbs used in professional resumes
    ACTION_VERBS = {
        "achieved", "improved", "trained", "managed", "created", "resolved",
        "developed", "implemented", "led", "architected", "optimized", "designed",
        "built", "engineered", "analyzed", "increased", "reduced", "launched",
        "established", "coordinated", "streamlined", "initiated", "executed",
        "delivered", "spearheaded", "drove", "transformed", "enhanced"
    }
    
    # Essential resume sections for ATS compliance
    REQUIRED_SECTIONS = {
        "summary", "skills", "experience", "education"
    }
    
    def calculate_ats_score(
        self,
        resume_content: ResumeContent,
        job_description: str = None,
        target_role: str = None
    ) -> ATSScore:
        """
        Calculate comprehensive ATS score based on multiple factors
        
        Args:
            resume_content: Structured resume content
            job_description: Optional job description for keyword matching
            target_role: Target job role for alignment
            
        Returns:
            ATSScore object with detailed scoring breakdown
        """
        
        # Calculate individual score components
        skill_match_score = self._calculate_skill_match(resume_content, job_description)
        keyword_score = self._calculate_keyword_relevance(resume_content, job_description)
        role_alignment_score = self._calculate_role_alignment(resume_content, target_role, job_description)
        formatting_score = self._calculate_formatting_score(resume_content)
        section_score = self._calculate_section_completeness(resume_content)
        
        # Calculate weighted overall score
        overall_score = int(
            (skill_match_score * 0.25) +
            (keyword_score * 0.25) +
            (role_alignment_score * 0.20) +
            (formatting_score * 0.15) +
            (section_score * 0.15)
        )
        
        # Generate explanation and suggestions
        explanation = self._generate_explanation(
            overall_score, skill_match_score, keyword_score,
            role_alignment_score, formatting_score, section_score
        )
        
        missing_keywords = self._identify_missing_keywords(resume_content, job_description)
        suggestions = self._generate_suggestions(
            skill_match_score, keyword_score, role_alignment_score,
            formatting_score, section_score
        )
        
        return ATSScore(
            overall_score=overall_score,
            skill_match=skill_match_score,
            keyword_relevance=keyword_score,
            role_alignment=role_alignment_score,
            formatting_score=formatting_score,
            section_completeness=section_score,
            explanation=explanation,
            missing_keywords=missing_keywords,
            suggestions=suggestions
        )
    
    def _calculate_skill_match(self, resume_content: ResumeContent, job_description: str = None) -> int:
        """Calculate skill match percentage"""
        if not job_description or not resume_content.skills:
            # Base score if no JD provided
            return min(len(resume_content.skills) * 8, 100)
        
        # Extract skills from job description
        jd_skills = self._extract_skills_from_text(job_description)
        resume_skills = set(skill.lower() for skill in resume_content.skills)
        
        if not jd_skills:
            return min(len(resume_content.skills) * 8, 100)
        
        # Calculate match percentage
        matched_skills = resume_skills.intersection(jd_skills)
        match_percentage = (len(matched_skills) / len(jd_skills)) * 100
        
        return min(int(match_percentage), 100)
    
    def _calculate_keyword_relevance(self, resume_content: ResumeContent, job_description: str = None) -> int:
        """Calculate keyword relevance score"""
        if not job_description:
            return 75  # Default score without JD
        
        # Extract keywords from JD
        jd_keywords = self._extract_keywords(job_description)
        
        # Extract keywords from resume
        resume_text = self._resume_to_text(resume_content)
        resume_keywords = self._extract_keywords(resume_text)
        
        if not jd_keywords:
            return 75
        
        # Calculate keyword overlap
        matched_keywords = resume_keywords.intersection(jd_keywords)
        relevance_score = (len(matched_keywords) / len(jd_keywords)) * 100
        
        return min(int(relevance_score), 100)
    
    def _calculate_role_alignment(self, resume_content: ResumeContent, target_role: str = None, job_description: str = None) -> int:
        """Calculate role alignment score"""
        score = 0
        
        # Check if summary mentions target role
        if target_role and resume_content.summary:
            if target_role.lower() in resume_content.summary.lower():
                score += 20
        
        # Check for relevant experience
        if resume_content.experience:
            score += min(len(resume_content.experience) * 15, 40)
        
        # Check for action verbs usage
        resume_text = self._resume_to_text(resume_content).lower()
        action_verb_count = sum(1 for verb in self.ACTION_VERBS if verb in resume_text)
        score += min(action_verb_count * 3, 30)
        
        # Check for quantifiable achievements
        numbers_count = len(re.findall(r'\d+%|\d+\+|\$\d+|\d+ [a-zA-Z]', resume_text))
        score += min(numbers_count * 2, 10)
        
        return min(score, 100)
    
    def _calculate_formatting_score(self, resume_content: ResumeContent) -> int:
        """Calculate formatting compliance score"""
        score = 100
        
        # Check for common ATS issues
        resume_text = self._resume_to_text(resume_content)
        
        # Penalize special characters (ATS systems prefer simple text)
        special_chars = len(re.findall(r'[★●◆■□▪►]', resume_text))
        score -= min(special_chars * 5, 20)
        
        # Check for proper section structure
        if not resume_content.summary or len(resume_content.summary) < 50:
            score -= 10
        
        # Reward consistent formatting (check experience entries)
        if resume_content.experience:
            has_consistent_format = all(
                exp.title and exp.company and exp.duration
                for exp in resume_content.experience
            )
            if not has_consistent_format:
                score -= 15
        
        return max(score, 0)
    
    def _calculate_section_completeness(self, resume_content: ResumeContent) -> int:
        """Calculate section completeness score"""
        score = 0
        
        # Required sections
        if resume_content.summary:
            score += 20
        if resume_content.skills and len(resume_content.skills) >= 5:
            score += 20
        if resume_content.experience:
            score += 25
        if resume_content.education:
            score += 15
        
        # Optional but valuable sections
        if resume_content.projects:
            score += 10
        if resume_content.certifications:
            score += 5
        if resume_content.achievements:
            score += 5
        
        return min(score, 100)
    
    def _extract_skills_from_text(self, text: str) -> Set[str]:
        """Extract potential skills from text"""
        # Common technical skills and keywords
        common_skills = {
            "python", "java", "javascript", "react", "node", "sql", "aws",
            "docker", "kubernetes", "git", "agile", "scrum", "machine learning",
            "data analysis", "project management", "leadership", "communication",
            "problem solving", "teamwork", "html", "css", "typescript", "mongodb",
            "postgresql", "redis", "ci/cd", "devops", "terraform", "jenkins"
        }
        
        text_lower = text.lower()
        found_skills = set()
        
        for skill in common_skills:
            if skill in text_lower:
                found_skills.add(skill)
        
        return found_skills
    
    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract meaningful keywords from text"""
        # Remove common words and extract important terms
        text_lower = text.lower()
        words = re.findall(r'\b[a-z]{3,}\b', text_lower)
        
        # Common stop words to exclude
        stop_words = {
            "the", "and", "for", "with", "this", "that", "from", "will",
            "have", "has", "are", "was", "were", "been", "being", "can",
            "could", "would", "should", "may", "might", "must", "our", "their"
        }
        
        keywords = set(word for word in words if word not in stop_words)
        return keywords
    
    def _resume_to_text(self, resume_content: ResumeContent) -> str:
        """Convert resume content to plain text for analysis"""
        text_parts = [resume_content.summary]
        
        text_parts.extend(resume_content.skills)
        
        for exp in resume_content.experience:
            text_parts.append(exp.title if exp.title else '')
            text_parts.append(exp.company if exp.company else '')
            text_parts.extend(exp.responsibilities if exp.responsibilities else [])
        
        for edu in resume_content.education:
            text_parts.append(edu.degree if edu.degree else '')
            text_parts.append(edu.institution if edu.institution else '')
        
        for proj in resume_content.projects:
            text_parts.append(proj.name if proj.name else '')
            text_parts.append(proj.description if proj.description else '')
        
        text_parts.extend(resume_content.certifications)
        text_parts.extend(resume_content.achievements)
        
        return ' '.join(text_parts)
    
    def _generate_explanation(
        self, overall: int, skill: int, keyword: int,
        role: int, formatting: int, section: int
    ) -> str:
        """Generate human-readable explanation of the score"""
        
        if overall >= 90:
            level = "Excellent"
            message = "Your resume is highly optimized for ATS systems and should pass most screenings."
        elif overall >= 75:
            level = "Good"
            message = "Your resume is well-optimized for ATS with room for minor improvements."
        elif overall >= 60:
            level = "Fair"
            message = "Your resume meets basic ATS requirements but could benefit from optimization."
        else:
            level = "Needs Improvement"
            message = "Your resume needs significant optimization to pass ATS screenings effectively."
        
        breakdown = f"""
Overall ATS Score: {overall}/100 ({level})

{message}

Score Breakdown:
• Skill Match: {skill}/100
• Keyword Relevance: {keyword}/100
• Role Alignment: {role}/100
• Formatting Compliance: {formatting}/100
• Section Completeness: {section}/100
"""
        return breakdown.strip()
    
    def _identify_missing_keywords(self, resume_content: ResumeContent, job_description: str = None) -> List[str]:
        """Identify important keywords missing from resume"""
        if not job_description:
            return []
        
        jd_keywords = self._extract_keywords(job_description)
        resume_text = self._resume_to_text(resume_content)
        resume_keywords = self._extract_keywords(resume_text)
        
        missing = list(jd_keywords - resume_keywords)[:10]  # Top 10 missing keywords
        return missing
    
    def _generate_suggestions(
        self, skill: int, keyword: int, role: int,
        formatting: int, section: int
    ) -> List[str]:
        """Generate actionable suggestions for improvement"""
        suggestions = []
        
        if skill < 70:
            suggestions.append("Add more relevant technical skills from the job description")
        
        if keyword < 70:
            suggestions.append("Incorporate more keywords from the job description throughout your resume")
        
        if role < 70:
            suggestions.append("Use stronger action verbs and quantify your achievements with metrics")
        
        if formatting < 80:
            suggestions.append("Simplify formatting - avoid special characters and complex layouts")
        
        if section < 80:
            suggestions.append("Add missing sections like Projects, Certifications, or Achievements")
        
        if not suggestions:
            suggestions.append("Great job! Your resume is well-optimized for ATS systems")
        
        return suggestions