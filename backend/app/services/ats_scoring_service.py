"""
ATS Scoring Service – FAANG-Grade
8-component scoring aligned with Google / Meta / Amazon ATS patterns.
AI-generated personalised suggestions via Gemini.
"""
from backend.app.models.schemas import ATSScore, ResumeContent
from backend.app.core.config import settings
from typing import List, Set
import re
from google import genai
from google.genai import types


class ATSScoringService:

    # ── Expanded action-verb library (100+) ───────────────────────────
    ACTION_VERBS = {
        # Engineering
        "architected","engineered","built","developed","implemented","deployed",
        "automated","optimized","refactored","migrated","integrated","designed",
        "coded","programmed","shipped","launched","released","scaled","debugged",
        # Leadership
        "led","managed","mentored","coached","directed","spearheaded","championed",
        "established","founded","initiated","drove","oversaw","supervised",
        # Impact
        "increased","reduced","improved","accelerated","boosted","cut","saved",
        "delivered","achieved","exceeded","generated","streamlined","enhanced",
        # Analysis
        "analyzed","evaluated","assessed","researched","investigated","identified",
        "diagnosed","resolved","troubleshot","discovered",
        # Collaboration
        "collaborated","coordinated","partnered","liaised","facilitated","aligned",
        "negotiated","presented","communicated","trained",
    }

    # ── FAANG-critical hard skills ─────────────────────────────────────
    FAANG_SKILLS = {
        "python","java","golang","c++","scala","kotlin","swift","javascript","typescript",
        "react","node","django","spring","fastapi","flask","kubernetes","docker","terraform",
        "aws","gcp","azure","spark","kafka","redis","postgresql","mysql","mongodb","cassandra",
        "elasticsearch","grpc","rest","graphql","microservices","system design","ci/cd",
        "agile","scrum","data structures","algorithms","machine learning","deep learning",
        "sql","nosql","distributed systems","devops","cloud","git","linux",
    }

    def __init__(self):
        try:
            self.client   = genai.Client(api_key=settings.GEMINI_API_KEY)
            self.model_id = 'gemini-2.5-flash'
            self.ai_ok    = True
        except Exception:
            self.ai_ok = False

    # ──────────────────────────────────────────────────────────────────
    def calculate_ats_score(
        self,
        resume_content: ResumeContent,
        job_description: str = None,
        target_role: str     = None,
    ) -> ATSScore:

        resume_text = self._to_text(resume_content)

        # ── 8 components ──────────────────────────────────────────────
        skill_match        = self._skill_match(resume_content, job_description)
        keyword_relevance  = self._keyword_density(resume_content, job_description)
        role_alignment     = self._role_alignment(resume_content, target_role, job_description)
        formatting_score   = self._formatting(resume_content)
        section_complete   = self._section_completeness(resume_content)
        action_verb_score  = self._action_verb_score(resume_text)
        quantified_score   = self._quantified_impact(resume_text)
        faang_compliance   = self._faang_compliance(resume_content, job_description)

        # ── Weighted overall (FAANG-tuned weights) ────────────────────
        overall = int(
            skill_match       * 0.20 +
            keyword_relevance * 0.18 +
            role_alignment    * 0.15 +
            formatting_score  * 0.10 +
            section_complete  * 0.10 +
            action_verb_score * 0.10 +
            quantified_score  * 0.10 +
            faang_compliance  * 0.07
        )

        missing_kw = self._missing_keywords(resume_content, job_description)

        # ── AI suggestions ────────────────────────────────────────────
        suggestions = self._ai_suggestions(
            resume_content, job_description, target_role,
            {
                "overall":          overall,
                "skill_match":      skill_match,
                "keyword":          keyword_relevance,
                "role_alignment":   role_alignment,
                "formatting":       formatting_score,
                "sections":         section_complete,
                "action_verbs":     action_verb_score,
                "quantified":       quantified_score,
                "faang":            faang_compliance,
                "missing_keywords": missing_kw,
            }
        )

        explanation = self._explanation(overall)

        return ATSScore(
            overall_score=overall,
            skill_match=skill_match,
            keyword_relevance=keyword_relevance,
            role_alignment=role_alignment,
            formatting_score=formatting_score,
            section_completeness=section_complete,
            action_verb_score=action_verb_score,
            quantified_score=quantified_score,
            faang_compliance=faang_compliance,
            explanation=explanation,
            missing_keywords=missing_kw,
            suggestions=suggestions,
        )

    # ─────────────── Component scorers ───────────────────────────────

    def _skill_match(self, rc: ResumeContent, jd: str) -> int:
        resume_skills = {s.lower() for s in rc.skills}
        if jd:
            jd_skills = {s for s in self.FAANG_SKILLS if s in jd.lower()}
        else:
            jd_skills = set()

        if not jd_skills:
            # Score based on FAANG skill density even without JD
            matched = resume_skills & self.FAANG_SKILLS
            return min(int(len(matched) / max(len(resume_skills), 1) * 100) + 30, 100)

        matched = resume_skills & jd_skills
        base    = int(len(matched) / len(jd_skills) * 100)
        # Bonus: extra FAANG skills in resume not required but valued
        bonus   = min(len(resume_skills & self.FAANG_SKILLS) * 2, 15)
        return min(base + bonus, 100)

    def _keyword_density(self, rc: ResumeContent, jd: str) -> int:
        if not jd:
            return 70
        jd_kw   = self._keywords(jd)
        res_kw  = self._keywords(self._to_text(rc))
        if not jd_kw:
            return 70
        overlap = len(res_kw & jd_kw)
        raw     = int(overlap / len(jd_kw) * 100)
        # FAANG ATS penalises keyword stuffing (>90% overlap is suspicious)
        return min(raw, 95)

    def _role_alignment(self, rc: ResumeContent, role: str, jd: str) -> int:
        score = 0
        txt   = self._to_text(rc).lower()

        if role:
            role_words = role.lower().split()
            matches    = sum(1 for w in role_words if w in txt)
            score     += int(matches / max(len(role_words), 1) * 25)

        if rc.experience:
            score += min(len(rc.experience) * 12, 36)

        if jd:
            jd_kw  = self._keywords(jd)
            res_kw = self._keywords(txt)
            score += min(int(len(res_kw & jd_kw) / max(len(jd_kw), 1) * 25), 25)

        return min(score, 100)

    def _formatting(self, rc: ResumeContent) -> int:
        score = 100
        txt   = self._to_text(rc)

        # Penalise ATS-breaking characters
        bad_chars = len(re.findall(r'[★●◆■□▪►|{}]', txt))
        score -= min(bad_chars * 4, 25)

        # Summary length check (FAANG expects 40-300 chars)
        if not rc.summary or len(rc.summary) < 40:
            score -= 15
        elif len(rc.summary) > 800:
            score -= 5

        # Consistent experience format
        if rc.experience:
            for exp in rc.experience:
                if not exp.title or not exp.company or not exp.duration:
                    score -= 8
                    break

        # Bullet count quality (FAANG expects 3-6 bullets per role)
        for exp in rc.experience:
            if len(exp.responsibilities) < 2:
                score -= 5
            elif len(exp.responsibilities) > 8:
                score -= 3

        return max(score, 0)

    def _section_completeness(self, rc: ResumeContent) -> int:
        score = 0
        if rc.summary:                              score += 18
        if rc.skills and len(rc.skills) >= 5:       score += 18
        if rc.experience:                           score += 22
        if rc.education:                            score += 14
        if rc.projects:                             score += 12
        if rc.certifications and len(rc.certifications) > 0: score += 8
        if rc.achievements  and len(rc.achievements)  > 0:   score += 8
        return min(score, 100)

    def _action_verb_score(self, txt: str) -> int:
        words = set(re.findall(r'\b[a-z]+\b', txt.lower()))
        hits  = words & self.ACTION_VERBS
        # FAANG expects 8+ unique action verbs
        score = min(int(len(hits) / 8 * 100), 100)
        return score

    def _quantified_impact(self, txt: str) -> int:
        # Count numeric metrics: %, $, x, K, M, numbers with units
        metrics = re.findall(
            r'\b\d+(?:\.\d+)?(?:%|x|X|\+|K|M|B|\s?(?:percent|million|billion|users|requests|ms|seconds|hours|days|teams|members|points))\b',
            txt, re.IGNORECASE
        )
        simple_nums = re.findall(r'\b\d{2,}\b', txt)  # numbers >= 10
        total = len(metrics) * 10 + len(simple_nums) * 3
        return min(total, 100)

    def _faang_compliance(self, rc: ResumeContent, jd: str) -> int:
        """FAANG-specific compliance: length, format, impact density."""
        score = 100
        txt   = self._to_text(rc)
        words = txt.split()

        # Resume length: 400-700 words ideal for 0-5 yr, up to 1000 for 10+ yr
        wc = len(words)
        if wc < 200:   score -= 25
        elif wc < 350: score -= 10
        elif wc > 1200: score -= 10

        # Phone & email present
        if not (rc.contact.phone and rc.contact.email):
            score -= 10

        # GitHub / LinkedIn (highly valued at FAANG)
        if not rc.contact.github and not rc.contact.linkedin:
            score -= 8

        # At least one project
        if not rc.projects:
            score -= 10

        # Education present
        if not rc.education:
            score -= 8

        # At least 6 FAANG skills
        faang_hits = sum(1 for s in rc.skills if s.lower() in self.FAANG_SKILLS)
        if faang_hits < 4:
            score -= 12
        elif faang_hits < 6:
            score -= 5

        return max(score, 0)

    # ─────────────── AI-powered suggestions ──────────────────────────

    def _ai_suggestions(
        self,
        rc: ResumeContent,
        jd: str,
        role: str,
        scores: dict,
    ) -> List[str]:
        """Call Gemini to generate personalised, actionable ATS suggestions."""

        if not self.ai_ok:
            return self._fallback_suggestions(scores)

        # Build a compact resume summary for the AI
        resume_summary = f"""
Name: {rc.full_name}
Role: {role or 'Not specified'}
Skills: {', '.join(rc.skills[:15]) if rc.skills else 'None'}
Experience positions: {len(rc.experience)}
Education entries: {len(rc.education)}
Projects: {len(rc.projects)}
Certifications: {len(rc.certifications)}
Achievements: {len(rc.achievements)}
Summary excerpt: {rc.summary[:200] if rc.summary else 'Missing'}
Missing JD keywords: {', '.join(scores.get('missing_keywords', [])[:8]) if scores.get('missing_keywords') else 'None'}
"""

        score_summary = f"""
Overall ATS: {scores['overall']}/100
Skill Match: {scores['skill_match']}/100
Keyword Density: {scores['keyword']}/100
Role Alignment: {scores['role_alignment']}/100
Formatting: {scores['formatting']}/100
Section Completeness: {scores['sections']}/100
Action Verb Usage: {scores['action_verbs']}/100
Quantified Impact: {scores['quantified']}/100
FAANG Compliance: {scores['faang']}/100
"""

        prompt = f"""You are a FAANG resume coach. Analyse this candidate's ATS report and generate 5-7 specific, actionable improvement suggestions.

RESUME DATA:
{resume_summary}

ATS SCORE BREAKDOWN:
{score_summary}

JOB DESCRIPTION SNIPPET:
{(jd or 'Not provided')[:400]}

REQUIREMENTS:
- Each suggestion must be concrete and specific to THIS resume (not generic advice)
- Prioritise the lowest-scoring components
- Suggest specific keywords, verbs, or sections to add
- Reference actual gaps you see (e.g. "Your skills list has Python but no mention of system design")
- Each suggestion should be 1-2 sentences max
- Format: Return a strictly valid JSON array of strings: ["suggestion 1", "suggestion 2"]
- VERY IMPORTANT: Return ONLY JSON. Do not include raw newlines or unescaped quotes inside the strings.
"""

        try:
            config = types.GenerateContentConfig(
                temperature=0.5,
                max_output_tokens=1024,
                response_mime_type="application/json",
            )
            resp = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=config,
            )
            
            import json, re as re2
            raw = resp.text.strip()
            
            # Clean up any potential markdown blocks
            raw = re2.sub(r'^```[a-zA-Z]*\s*', '', raw)
            raw = re2.sub(r'\s*```$', '', raw).strip()
            
            # Force extract just the JSON array to avoid conversational text breaking the parser
            match = re2.search(r'\[.*\]', raw, re2.DOTALL)
            if match:
                raw = match.group(0)
                
            # strict=False allows raw newlines inside strings without throwing Unterminated string errors
            data = json.loads(raw, strict=False)
            
            if isinstance(data, list):
                return [str(s) for s in data[:8]]
                
            return self._fallback_suggestions(scores)
            
        except Exception as e:
            print(f"⚠️ AI suggestions failed: {e}")
            return self._fallback_suggestions(scores)

    def _fallback_suggestions(self, scores: dict) -> List[str]:
        out = []
        if scores['skill_match'] < 60:
            out.append("Add more technical skills from the job description — especially cloud (AWS/GCP), data structures, and system design keywords.")
        if scores['quantified'] < 50:
            out.append("Add quantified metrics to your bullet points (e.g. '40% reduction in latency', 'served 1M+ users') — FAANG recruiters look for measurable impact.")
        if scores['action_verbs'] < 60:
            out.append("Replace weak phrases like 'responsible for' or 'worked on' with strong action verbs: Architected, Optimized, Deployed, Led, Reduced.")
        if scores['sections'] < 80:
            out.append("Add missing sections — at minimum include: Summary, Skills, Experience, Education, and at least one Project.")
        if scores['faang'] < 70:
            out.append("Add your GitHub and LinkedIn URLs — these significantly improve FAANG ATS ranking. Also ensure phone and email are present.")
        if scores['keyword'] < 60:
            out.append("Your resume has low keyword density vs the job description. Weave JD terms naturally into bullet points and your summary.")
        if not out:
            out.append("Great score! To push above 90, add more quantified metrics and ensure GitHub/LinkedIn links are visible.")
        return out

    # ─────────────── Utilities ────────────────────────────────────────

    def _keywords(self, text: str) -> Set[str]:
        STOP = {
            "the","and","for","with","this","that","from","will","have","has",
            "are","was","were","been","being","can","could","would","should",
            "may","might","must","our","their","you","your","they","them",
            "not","but","all","any","each","into","than","then","its","also",
        }
        words = re.findall(r'\b[a-z][a-z0-9+#\-\.]*\b', text.lower())
        return {w for w in words if len(w) >= 3 and w not in STOP}

    def _to_text(self, rc: ResumeContent) -> str:
        parts = [rc.summary or '']
        parts += list(rc.skills or [])
        for e in (rc.experience or []):
            parts += [e.title, e.company] + list(e.responsibilities or [])
        for e in (rc.education or []):
            parts += [e.degree, e.institution]
        for p in (rc.projects or []):
            parts += [p.name, p.description, p.technologies, p.impact]
        parts += list(rc.certifications or [])
        parts += list(rc.achievements or [])
        return ' '.join(x for x in parts if x)

    def _missing_keywords(self, rc: ResumeContent, jd: str) -> List[str]:
        if not jd:
            return []
        jd_kw  = self._keywords(jd)
        res_kw = self._keywords(self._to_text(rc))
        missing = sorted(jd_kw - res_kw)
        # Filter to meaningful words only (>= 4 chars, not pure stop words)
        return [w for w in missing if len(w) >= 4][:12]

    def _explanation(self, score: int) -> str:
        if score >= 85:
            return f"Score: {score}/100 — Excellent. FAANG-ready. This resume should pass most ATS filters including Google, Meta, Amazon."
        elif score >= 70:
            return f"Score: {score}/100 — Good. Competitive profile. A few targeted improvements will push you into the top 15% of applicants."
        elif score >= 55:
            return f"Score: {score}/100 — Fair. Will pass basic ATS but be filtered at FAANG-level. Follow the suggestions to improve."
        else:
            return f"Score: {score}/100 — Below threshold. Significant gaps vs FAANG ATS standards. Prioritise the suggestions below."