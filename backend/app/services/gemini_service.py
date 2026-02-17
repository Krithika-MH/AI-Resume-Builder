"""
Gemini AI Service for Resume Generation
Uses REAL user-provided data – AI only polishes wording, never invents facts.
"""
from google import genai
from google.genai import types
from backend.app.core.config import settings
from backend.app.models.schemas import (
    ResumeContent, ContactInfo, ExperienceItem,
    EducationItem, ProjectItem
)
import json
import re


class GeminiService:
    def __init__(self):
        self.client   = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_id = 'gemini-2.5-flash'
        print(f"✅ Gemini Service initialized with model: {self.model_id}")

    # ------------------------------------------------------------------ #
    #  PUBLIC: main entry point                                            #
    # ------------------------------------------------------------------ #
    def generate_resume_content(
        self,
        full_name:            str,
        phone:                str,
        email:                str,
        target_role:          str,
        job_description:      str  = None,
        existing_resume_text: str  = None,
        user_data:            dict = None,   # ← structured form data
    ) -> ResumeContent:

        print(f"\n🤖 Generating resume for: {full_name}  |  Role: {target_role}")

        # ── Build prompt ──────────────────────────────────────────────
        prompt = self._build_prompt(
            full_name, phone, email, target_role,
            job_description, existing_resume_text, user_data
        )

        try:
            config = types.GenerateContentConfig(
                temperature=0.4,          # lower temp → less hallucination
                top_p=0.95,
                max_output_tokens=8192,
                response_mime_type="application/json",
            )

            print("📡 Calling Gemini API…")
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=config,
            )

            raw = response.text
            print(f"✅ Received {len(raw)} chars")

            data = self._parse_json(raw)
            if not data:
                raise ValueError("Empty / unparseable response")

            return self._build_resume_content(
                full_name, phone, email, target_role,
                data, user_data
            )

        except Exception as e:
            print(f"❌ Gemini error: {e}")
            import traceback; traceback.print_exc()
            # Fall back to whatever the user typed, unpolished
            return self._build_from_raw_user_data(
                full_name, phone, email, target_role, user_data
            )

    # ------------------------------------------------------------------ #
    #  Prompt builder                                                      #
    # ------------------------------------------------------------------ #
    def _build_prompt(
        self,
        full_name, phone, email, target_role,
        job_description, existing_resume_text, user_data,
    ) -> str:

        # ── Summarise what the user actually gave us ──────────────────
        ud = user_data or {}

        lines = [
            f"You are a professional resume writer. Your task is ONLY to polish and",
            f"professionally reword the information below — do NOT invent or add any",
            f"facts, companies, schools, dates, or projects that are not provided.",
            f"",
            f"=== CANDIDATE DETAILS ===",
            f"Name        : {full_name}",
            f"Phone       : {phone}",
            f"Email       : {email}",
            f"Target Role : {target_role}",
        ]

        if ud.get('linkedin'):  lines.append(f"LinkedIn    : {ud['linkedin']}")
        if ud.get('github'):    lines.append(f"GitHub      : {ud['github']}")

        # Summary hint
        if ud.get('summary'):
            lines += ["", "=== PROFESSIONAL SUMMARY (user-written – improve wording) ===",
                      ud['summary']]
        else:
            lines += ["", "=== PROFESSIONAL SUMMARY ===",
                      f"Write a 3-sentence professional summary for a {target_role} based ONLY on",
                      "the skills, experience, and education listed below. Do NOT mention",
                      "companies or achievements that aren't listed."]

        # Skills
        tech = ud.get('tech_skills', [])
        soft = ud.get('soft_skills', [])
        all_skills = tech + soft
        if all_skills:
            lines += ["", "=== SKILLS (use exactly these, do not add more) ===",
                      ", ".join(all_skills)]
        else:
            lines += ["", "=== SKILLS ===",
                      "No skills provided. Generate 8 common skills for this role."]

        # Experience
        exp_list = ud.get('experience', [])
        if exp_list:
            lines += ["", "=== WORK EXPERIENCE (polish bullets, keep all facts exact) ==="]
            for i, e in enumerate(exp_list, 1):
                lines.append(f"\n-- Position {i} --")
                lines.append(f"Title    : {e.get('title','')}")
                lines.append(f"Company  : {e.get('company','')}")
                lines.append(f"Duration : {e.get('duration','')}")
                lines.append(f"Location : {e.get('location','')}")
                resps = e.get('responsibilities', [])
                if resps:
                    lines.append("Bullets (improve wording, keep meaning):")
                    for r in resps:
                        lines.append(f"  - {r}")
                else:
                    lines.append("No bullets given. Write 3 generic bullets for this role/company.")
        else:
            lines += ["", "=== WORK EXPERIENCE ===",
                      "No experience provided. Leave experience list empty ([])."]

        # Education
        edu_list = ud.get('education', [])
        if edu_list:
            lines += ["", "=== EDUCATION ==="]
            for i, e in enumerate(edu_list, 1):
                lines.append(f"\n-- Entry {i} --")
                lines.append(f"Degree      : {e.get('degree','')}")
                lines.append(f"Institution : {e.get('institution','')}")
                lines.append(f"Year        : {e.get('year','')}")
                lines.append(f"GPA         : {e.get('gpa','')}")
        else:
            lines += ["", "=== EDUCATION ===",
                      "No education provided. Leave education list empty ([])."]

        # Projects
        proj_list = ud.get('projects', [])
        if proj_list:
            lines += ["", "=== PROJECTS ==="]
            for i, p in enumerate(proj_list, 1):
                lines.append(f"\n-- Project {i} --")
                lines.append(f"Name         : {p.get('name','')}")
                lines.append(f"Technologies : {p.get('technologies','')}")
                lines.append(f"Description  : {p.get('description','')}")
                lines.append(f"Impact       : {p.get('impact','')}")
        else:
            lines += ["", "=== PROJECTS ===",
                      "No projects provided. Leave projects list empty ([])."]

        # Certifications
        certs = ud.get('certifications', [])
        if certs:
            lines += ["", "=== CERTIFICATIONS (use exactly as given) ==="] + certs
        else:
            lines += ["", "=== CERTIFICATIONS ===", "None provided. Leave empty ([])."]

        # Achievements
        achs = ud.get('achievements', [])
        if achs:
            lines += ["", "=== ACHIEVEMENTS (use exactly as given) ==="] + achs
        else:
            lines += ["", "=== ACHIEVEMENTS ===", "None provided. Leave empty ([])."]

        # Job description
        if job_description:
            lines += ["", "=== JOB DESCRIPTION (align keywords only – don't invent) ===",
                      job_description[:800]]

        # Existing resume
        if existing_resume_text:
            lines += ["", "=== EXISTING RESUME TEXT (extract real facts from here) ===",
                      existing_resume_text[:1500]]

        # Output format
        lines += [
            "",
            "=== OUTPUT FORMAT ===",
            "Return ONLY valid JSON matching this schema exactly:",
            '{',
            '  "summary": "string",',
            '  "skills": ["string", ...],',
            '  "experience": [{"title":"","company":"","duration":"","location":"","responsibilities":["..."]}],',
            '  "education":  [{"degree":"","institution":"","year":"","gpa":""}],',
            '  "projects":   [{"name":"","description":"","technologies":"","impact":""}],',
            '  "certifications": ["string"],',
            '  "achievements":   ["string"],',
            '  "linkedin": "",',
            '  "github":   ""',
            '}',
            "",
            "RULES:",
            "1. Do NOT invent companies, dates, schools, or projects not listed above.",
            "2. DO improve grammar, add action verbs, and add metrics ONLY when clearly implied.",
            "3. Keep every fact exactly as given.",
            "4. If a section is empty above, output an empty list [] for it.",
        ]

        return "\n".join(lines)

    # ------------------------------------------------------------------ #
    #  Parse Gemini response                                               #
    # ------------------------------------------------------------------ #
    def _parse_json(self, raw: str) -> dict:
        try:
            cleaned = raw.strip()
            cleaned = re.sub(r'^```json\s*', '', cleaned)
            cleaned = re.sub(r'^```\s*', '', cleaned)
            cleaned = re.sub(r'```\s*$', '', cleaned).strip()
            data = json.loads(cleaned)
            if 'summary' in data or 'skills' in data:
                print("✅ JSON parsed OK")
                return data
            return {}
        except Exception as e:
            print(f"❌ JSON parse error: {e}")
            print("First 400 chars:", raw[:400])
            return {}

    # ------------------------------------------------------------------ #
    #  Build ResumeContent from Gemini's polished JSON                    #
    # ------------------------------------------------------------------ #
    def _build_resume_content(
        self,
        full_name, phone, email, target_role,
        data: dict,
        user_data: dict,
    ) -> ResumeContent:
        ud = user_data or {}

        contact = ContactInfo(
            phone=phone,
            email=email,
            linkedin=ud.get('linkedin') or data.get('linkedin', ''),
            github=ud.get('github')   or data.get('github',   ''),
            portfolio=ud.get('portfolio', ''),
        )

        # Experience
        experience = []
        for e in data.get('experience', []):
            try:
                experience.append(ExperienceItem(
                    title=e.get('title', ''),
                    company=e.get('company', ''),
                    duration=e.get('duration', ''),
                    location=e.get('location', ''),
                    responsibilities=e.get('responsibilities', []),
                ))
            except Exception as ex:
                print(f"⚠️ Bad exp entry: {ex}")

        # Education
        education = []
        for e in data.get('education', []):
            try:
                education.append(EducationItem(
                    degree=e.get('degree', ''),
                    institution=e.get('institution', ''),
                    year=str(e.get('year', '')),
                    gpa=e.get('gpa') or None,
                ))
            except Exception as ex:
                print(f"⚠️ Bad edu entry: {ex}")

        # Projects
        projects = []
        for p in data.get('projects', []):
            try:
                projects.append(ProjectItem(
                    name=p.get('name', ''),
                    description=p.get('description', ''),
                    technologies=p.get('technologies', ''),
                    impact=p.get('impact', ''),
                ))
            except Exception as ex:
                print(f"⚠️ Bad proj entry: {ex}")

        rc = ResumeContent(
            full_name=full_name,
            contact=contact,
            summary=data.get('summary', ''),
            skills=data.get('skills', []),
            experience=experience,
            education=education,
            projects=projects,
            certifications=data.get('certifications', []),
            achievements=data.get('achievements', []),
        )

        print(f"  Summary chars : {len(rc.summary)}")
        print(f"  Skills        : {len(rc.skills)}")
        print(f"  Experience    : {len(rc.experience)}")
        print(f"  Education     : {len(rc.education)}")
        print(f"  Projects      : {len(rc.projects)}")
        return rc

    # ------------------------------------------------------------------ #
    #  Fallback: use raw user data without AI polishing                   #
    # ------------------------------------------------------------------ #
    def _build_from_raw_user_data(
        self,
        full_name, phone, email, target_role,
        user_data: dict,
    ) -> ResumeContent:
        print("⚠️  Using raw user data as fallback (no AI polish)")
        ud = user_data or {}

        contact = ContactInfo(
            phone=phone, email=email,
            linkedin=ud.get('linkedin', ''),
            github=ud.get('github', ''),
            portfolio=ud.get('portfolio', ''),
        )

        tech = ud.get('tech_skills', [])
        soft = ud.get('soft_skills', [])
        skills = tech + soft or [
            'Communication', 'Problem Solving', 'Team Collaboration',
            'Time Management', 'Critical Thinking',
        ]

        summary = ud.get('summary') or (
            f"Motivated professional seeking {target_role} role. "
            "Skilled in " + ", ".join(skills[:4]) + ". "
            "Committed to delivering high-quality results."
        )

        experience = []
        for e in ud.get('experience', []):
            if not e.get('title') and not e.get('company'):
                continue
            experience.append(ExperienceItem(
                title=e.get('title', target_role),
                company=e.get('company', ''),
                duration=e.get('duration', ''),
                location=e.get('location', ''),
                responsibilities=e.get('responsibilities', [
                    'Contributed to team projects and deliverables',
                    'Collaborated with stakeholders to meet requirements',
                ]),
            ))

        education = []
        for e in ud.get('education', []):
            if not e.get('degree') and not e.get('institution'):
                continue
            education.append(EducationItem(
                degree=e.get('degree', ''),
                institution=e.get('institution', ''),
                year=str(e.get('year', '')),
                gpa=e.get('gpa') or None,
            ))

        projects = []
        for p in ud.get('projects', []):
            if not p.get('name'):
                continue
            projects.append(ProjectItem(
                name=p.get('name', ''),
                description=p.get('description', ''),
                technologies=p.get('technologies', ''),
                impact=p.get('impact', ''),
            ))

        return ResumeContent(
            full_name=full_name,
            contact=contact,
            summary=summary,
            skills=skills,
            experience=experience,
            education=education,
            projects=projects,
            certifications=ud.get('certifications', []),
            achievements=ud.get('achievements', []),
        )