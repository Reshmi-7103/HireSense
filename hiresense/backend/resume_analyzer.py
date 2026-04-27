"""
PURPOSE: COORDINATOR ONLY - Orchestrates all modules, no heavy logic
"""

import os
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import docx

# Import all utility modules
from utils.pdf_parser import extract_text_from_pdf
from utils.text_cleaner import clean_text
from utils.skill_extractor import (
    load_job_dataset,
    build_global_skill_set,
    extract_resume_skills,
    compute_skill_match_score,
)
from utils.ats_cheaker import check_ats_compatibility
from utils.grammer_cheak import check_grammar
from utils.quality_cheak import check_content_quality
from utils.feedback_generator import generate_feedback
from utils.recommendation_engine import generate_recommendations


# ============================================================================
# DATA CLASS
# ============================================================================


@dataclass
class ResumeAnalysisResult:
    overall_score: float
    ats_score: float
    job_match_score: float
    skills_match_score: float
    content_quality_score: float
    resume_skills: List[str]
    missing_skills: List[str]
    matched_skills: List[str]
    sections_found: Dict[str, bool]
    grammar_errors: List[Dict]
    formatting_issues: List[str]
    feedback: List[str]
    recommendations: List[str]
    best_matching_job: Optional[Dict[str, Any]]


# ============================================================================
# MAIN ANALYZER CLASS
# ============================================================================


class ResumeAnalyzer:
    def __init__(self, job_data_path: str = None):
        """Initialize with job data and tools"""

        # Load job data
        if job_data_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            job_data_path = os.path.join(current_dir, "utils", "cleaned_job_posts.csv")

        self.job_df = load_job_dataset(job_data_path)
        self.global_skills = build_global_skill_set(self.job_df)

        # Initialize grammar tool
        try:
            import language_tool_python
            self.grammar_tool = language_tool_python.LanguageTool("en-US")
        except:
            self.grammar_tool = None

        self.action_verbs = [
            "achieved", "improved", "implemented", "developed", "managed", "created",
            "led", "increased", "reduced", "designed", "built", "optimized",
        ]

    # ========================================================================
    # TEXT EXTRACTION
    # ========================================================================

    def extract_text(self, file_path: str) -> str:
        """Extract text from PDF or Word"""
        ext = file_path.split(".")[-1].lower()
        if ext == "pdf":
            return extract_text_from_pdf(file_path)
        elif ext in ["docx", "doc"]:
            doc = docx.Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs])
        raise Exception(f"Unsupported: {ext}")

    # ========================================================================
    # SECTION EXTRACTION
    # ========================================================================

    def extract_sections(self, text: str) -> Dict[str, str]:
        """Extract sections from resume text"""
        text_lower = text.lower()
        sections = {
            "skills": "",
            "projects": "",
            "experience": "",
            "education": "",
            "summary": "",
        }

        # Skills section
        for keyword in ["technical skills", "skills"]:
            if keyword in text_lower:
                start = text_lower.find(keyword)
                sections["skills"] = text[start:start + 800]
                break

        # Projects section
        for keyword in ["projects", "project"]:
            if keyword in text_lower:
                start = text_lower.find(keyword)
                sections["projects"] = text[start:start + 800]
                break

        # Experience section
        if "experience" in text_lower:
            start = text_lower.find("experience")
            sections["experience"] = text[start:]

        # Education section
        if "education" in text_lower:
            start = text_lower.find("education")
            sections["education"] = text[start:start + 500]

        # Summary section
        for keyword in ["summary", "profile", "objective"]:
            if keyword in text_lower:
                start = text_lower.find(keyword)
                sections["summary"] = text[start:start + 300]
                break

        return sections

    # ========================================================================
    # SKILL EXTRACTION
    # ========================================================================

    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume"""
        sections = self.extract_sections(text)
        skills_text = sections.get("skills", "")

        # Simple cleaning for skill extraction
        skills_text = skills_text.lower()
        skills_text = re.sub(r"[^a-z0-9\s\+\.#\-]", " ", skills_text)
        skills_text = re.sub(r"\s+", " ", skills_text)

        skills = extract_resume_skills(skills_text, self.global_skills)
        return list(set(skills))[:15]

    # ========================================================================
    # JOB MATCHING - EXACT ROLE ONLY
    # ========================================================================

    def get_job_by_role(self, role: str) -> Optional[Dict[str, Any]]:
        """Find job by exact role name from CSV"""
        if not role:
            return None

        role_lower = role.lower()

        for _, row in self.job_df.iterrows():
            job_title = row.get("job_title", "").lower()
            if role_lower in job_title or job_title in role_lower:
                return {
                    "title": row.get("job_title"),
                    "description": row.get("job_description", ""),
                    "skills": [
                        s.strip().lower()
                        for s in str(row.get("job_skill_set", "")).split(",")
                        if s.strip()
                    ],
                }
        return None

    # ========================================================================
    # SIMILARITY SCORE
    # ========================================================================

    def compute_similarity_score(self, resume_text: str, job_desc: str) -> float:
        """Calculate similarity between resume and job description"""
        if not resume_text or not job_desc:
            return 0.0

        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        vectorizer = TfidfVectorizer(stop_words="english", lowercase=True)
        vectors = vectorizer.fit_transform([resume_text, job_desc])
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])

        return similarity[0][0] * 100

    # ========================================================================
    # MAIN ANALYSIS
    # ========================================================================

    def analyze_resume(
        self, file_path: str, role: str = None, **kwargs
    ) -> ResumeAnalysisResult:
        """Analyze resume against a specific job role"""

        # Extract text
        raw_text = self.extract_text(file_path)

        # Extract sections
        sections = self.extract_sections(raw_text)
        sections_found = {k: bool(v.strip()) for k, v in sections.items()}

        # Clean text
        cleaned_text = clean_text(raw_text)

        # Extract skills
        resume_skills = self.extract_skills(raw_text)

        # ATS Check
        ats_score, formatting_issues = check_ats_compatibility(raw_text)
        for sec, found in sections_found.items():
            if not found and sec in ["experience", "education", "skills"]:
                formatting_issues.append(f"Missing '{sec}' section")
                ats_score -= 15
        ats_score = max(0, ats_score)

        # Find job by role
        job = self.get_job_by_role(role) if role else None

        if job:
            job_skills = job["skills"]
            job_match_score = self.compute_similarity_score(
                cleaned_text, job["description"]
            )
            job_title = job["title"]

            # Calculate skill match
            skill_match_score = compute_skill_match_score(resume_skills, job_skills)
            resume_skills_lower = [s.lower() for s in resume_skills]
            matched_skills = [s for s in job_skills if s in resume_skills_lower]
            missing_skills = [s for s in job_skills if s not in resume_skills_lower][:10]
        else:
            job_title = role if role else "Not specified"
            job_skills = []
            job_match_score = 0
            skill_match_score = 0
            matched_skills = []
            missing_skills = []

        # Grammar Check
        grammar_count, grammar_details = check_grammar(raw_text, self.grammar_tool)

        # Content Quality
        content_quality_score, quality_suggestions = check_content_quality(raw_text, sections)

        # Fix variable name for feedback
        grammar_error_count = grammar_count
        grammar_error_details = grammar_details

        # Feedback & Recommendations
        feedback = generate_feedback(
            sections=sections,
            resume_skills=resume_skills,
            skill_match_score=skill_match_score,
            job_match_score=job_match_score,
            content_quality_score=content_quality_score,
            missing_skills=missing_skills,
            grammar_errors=grammar_error_count,
            ats_score=ats_score,
        )

        recommendations = generate_recommendations(
            missing_skills=missing_skills,
            sections=sections,
            grammar_errors=grammar_error_details,
            text=raw_text,
            action_verbs=self.action_verbs,
            ats_score=ats_score,
            skill_match_score=skill_match_score,
        )

        # Overall Score
        overall = (
            (ats_score * 0.2)
            + (job_match_score * 0.3)
            + (skill_match_score * 0.3)
            + (content_quality_score * 0.2)
        )

        # Result
        return ResumeAnalysisResult(
            overall_score=round(overall, 2),
            ats_score=round(ats_score, 2),
            job_match_score=round(job_match_score, 2),
            skills_match_score=round(skill_match_score, 2),
            content_quality_score=round(content_quality_score, 2),
            resume_skills=resume_skills,
            missing_skills=missing_skills,
            matched_skills=matched_skills,
            sections_found=sections_found,
            grammar_errors=grammar_details,
            formatting_issues=formatting_issues,
            feedback=feedback,
            recommendations=recommendations,
            best_matching_job=({"title": job_title, "skills": job_skills} if job else None),
        )

    # ========================================================================
    # REPORT GENERATION
    # ========================================================================

    def generate_report(self, result: ResumeAnalysisResult) -> Dict[str, Any]:
        """Generate clean report from results"""
        return {
            "summary": {
                "overall_score": result.overall_score,
                "ats_compatibility": result.ats_score,
                "job_match": result.job_match_score,
                "skills_match": result.skills_match_score,
                "content_quality": result.content_quality_score,
            },
            "skills_analysis": {
                "found": result.resume_skills,
                "missing": result.missing_skills,
                "matched": result.matched_skills,
                "match_percentage": result.skills_match_score,
            },
            "grammar_details": result.grammar_errors[:5],
            "formatting_issues": result.formatting_issues,
            "feedback": result.feedback,
            "recommendations": result.recommendations,
        }


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


def analyze_resume(file_path: str, role: str = None) -> Dict[str, Any]:
    """Simple function for backward compatibility"""
    analyzer = ResumeAnalyzer()
    result = analyzer.analyze_resume(file_path, role)
    return {
        "score": result.overall_score,
        "ats_score": result.ats_score,
        "job_match_score": result.job_match_score,
        "skills_match_score": result.skills_match_score,
        "skills": result.resume_skills,
        "missing_skills": result.missing_skills,
        "matched_skills": result.matched_skills,
        "feedback": result.feedback,
        "recommendations": result.recommendations,
        "grammar_errors": len(result.grammar_errors),
        "grammar_details": result.grammar_errors[:3],
    }