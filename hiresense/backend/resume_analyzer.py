# utils/resume_analyzer.py
"""
PURPOSE: COORDINATOR ONLY - Orchestrates all modules, no heavy logic
"""

import os
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Import all utility modules
from utils.pdf_parser import extract_text_from_pdf
from utils.text_cleaner import clean_text
from utils.skill_extracter import (
    load_job_dataset,
    build_global_skill_set,
    extract_resume_skills,
    compute_skill_match_score
)
from utils.similarity import compute_similarity
from utils.ats_cheaker import check_ats_compatibility
from utils.grammer_cheak import check_grammar
from utils.quality_cheak import check_content_quality
from utils.feedback_generator import generate_feedback
from utils.recommendation_engine import generate_recommendations

# Import for section extraction
import docx

# ============================================================================
# DATA CLASS - CLEAN OUTPUT STRUCTURE
# ============================================================================

@dataclass
class ResumeAnalysisResult:
    """Clean, structured output from analysis"""
    # Scores
    overall_score: float
    ats_score: float
    job_match_score: float
    skills_match_score: float
    content_quality_score: float
    
    # Skills
    resume_skills: List[str]
    missing_skills: List[str]
    matched_skills: List[str]
    
    # Content
    sections_found: Dict[str, bool]
    grammar_errors: List[Dict]  # ← Now contains DETAILED errors!
    formatting_issues: List[str]
    
    # Feedback
    feedback: List[str]
    recommendations: List[str]
    
    # Job match details
    best_matching_job: Optional[Dict[str, Any]]


# ============================================================================
# COORDINATOR CLASS - Only orchestrates, no heavy logic
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
            self.grammar_tool = language_tool_python.LanguageTool('en-US')
        except:
            self.grammar_tool = None
        
        # Action verbs list
        self.action_verbs = [
            'achieved', 'improved', 'implemented', 'developed', 'managed', 'created',
            'led', 'increased', 'reduced', 'designed', 'built', 'optimized'
        ]
    
    # ========================================================================
    # SECTION EXTRACTION (Simple - just finds sections)
    # ========================================================================
    
    def extract_sections(self, text: str) -> Dict[str, str]:
        """Simple section extraction - finds sections by keywords"""
        text_lower = text.lower()
        sections = {
            "skills": "",
            "projects": "",
            "experience": "",
            "education": "",
            "summary": ""
        }
        
        # Find skills section
        for keyword in ["technical skills", "skills"]:
            if keyword in text_lower:
                start = text_lower.find(keyword)
                sections["skills"] = text[start:start + 500]  # First 500 chars
                break
        
        # Find projects section
        for keyword in ["projects", "project"]:
            if keyword in text_lower:
                start = text_lower.find(keyword)
                sections["projects"] = text[start:start + 800]
                break
        
        # Find experience section
        for keyword in ["experience", "work experience"]:
            if keyword in text_lower:
                start = text_lower.find(keyword)
                sections["experience"] = text[start:]
                break
        
        # Find education section
        if "education" in text_lower:
            start = text_lower.find("education")
            sections["education"] = text[start:start + 500]
        
        # Find summary
        for keyword in ["summary", "profile", "objective"]:
            if keyword in text_lower:
                start = text_lower.find(keyword)
                sections["summary"] = text[start:start + 300]
                break
        
        return sections
    
    # ========================================================================
    # TEXT EXTRACTION
    # ========================================================================
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from PDF or Word"""
        ext = file_path.split('.')[-1].lower()
        if ext == 'pdf':
            return extract_text_from_pdf(file_path)
        elif ext in ['docx', 'doc']:
            doc = docx.Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs])
        raise Exception(f"Unsupported: {ext}")
    
    # ========================================================================
    # SKILL EXTRACTION
    # ========================================================================
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract skills using skill_extractor"""
        sections = self.extract_sections(text)
        skills_text = sections.get("skills", "")
        cleaned = clean_text(skills_text)
        skills = extract_resume_skills(cleaned, self.global_skills)
        return list(set(skills))[:15]
    
    # ========================================================================
    # JOB MATCHING
    # ========================================================================
    
    def find_best_job_match(self, cleaned_text: str, role: str = None) -> Dict[str, Any]:
        """Find best matching job using similarity.py"""
        if role:
            filtered = self.job_df[self.job_df["job_title"].str.contains(role, case=False, na=False)]
        else:
            filtered = self.job_df
        
        if filtered.empty:
            return {"found": False}
        
        job_descriptions = filtered["job_description"].fillna("").tolist()
        scores = compute_similarity(cleaned_text, job_descriptions)
        best_idx = scores.argmax()
        best_job = filtered.iloc[best_idx]
        
        return {
            "found": True,
            "job_title": best_job.get("job_title", "Unknown"),
            "similarity_score": round(scores[best_idx] * 100, 2),
            "job_skills": [s.strip().lower() for s in str(best_job.get("job_skill_set", "")).split(",") if s.strip()]
        }
    
    # ============================================================================
    # MAIN ANALYSIS - COORDINATES ALL MODULES
    # ============================================================================
    
    def analyze_resume(self, file_path: str, role: str = None, **kwargs) -> ResumeAnalysisResult:
        """
        COORDINATOR: Calls each specialized module and combines results
        """
        
        # STEP 1: Extract text
        raw_text = self.extract_text(file_path)
        
        # STEP 2: Extract sections
        sections = self.extract_sections(raw_text)
        sections_found = {k: bool(v.strip()) for k, v in sections.items()}
        
        # STEP 3: Clean text for matching
        cleaned_text = clean_text(raw_text)
        
        # STEP 4: Extract skills
        resume_skills = self.extract_skills(raw_text)
        
        # STEP 5: ATS Check (from ats_checker.py)
        ats_score, formatting_issues = check_ats_compatibility(raw_text)
        # Add missing sections to formatting issues
        for sec, found in sections_found.items():
            if not found and sec in ['experience', 'education', 'skills']:
                formatting_issues.append(f"Missing '{sec}' section")
                ats_score -= 15
        ats_score = max(0, ats_score)
        
        # STEP 6: Job Match (from similarity.py)
        job_match = self.find_best_job_match(cleaned_text, role)
        
        # STEP 7: Skill Match (from skill_extractor.py)
        if job_match.get("found"):
            job_skills = job_match.get("job_skills", [])
            skill_match_score = compute_skill_match_score(
                [s.lower() for s in resume_skills],
                job_skills
            )
            job_match_score = job_match.get("similarity_score", 0)
            # Calculate missing/matched skills
            resume_lower = [s.lower() for s in resume_skills]
            missing_skills = [s for s in job_skills if s not in resume_lower][:10]
            matched_skills = [s for s in job_skills if s in resume_lower][:10]
        else:
            skill_match_score = 0
            job_match_score = 0
            missing_skills = []
            matched_skills = []
        
        # STEP 8: Grammar Check (from grammar_checker.py - RETURNS DETAILS!)
        grammar_error_count, grammar_error_details = check_grammar(raw_text, self.grammar_tool)
        
        # STEP 9: Content Quality (from quality_checker.py)
        content_quality_score, quality_suggestions = check_content_quality(raw_text, sections)
        
        # STEP 10: Generate Feedback (from feedback_generator.py)
        feedback = generate_feedback(
            sections, resume_skills, skill_match_score, job_match_score, content_quality_score
        )
        
        # STEP 11: Generate Recommendations (from recommendation_engine.py)
        recommendations = generate_recommendations(
            missing_skills, sections, grammar_error_details, raw_text, self.action_verbs
        )
        
        # STEP 12: Calculate Overall Score
        overall_score = (
            ats_score * 0.20 +
            job_match_score * 0.30 +
            skill_match_score * 0.30 +
            content_quality_score * 0.20
        )
        
        # STEP 13: Return Clean Result
        return ResumeAnalysisResult(
            overall_score=round(overall_score, 2),
            ats_score=round(ats_score, 2),
            job_match_score=round(job_match_score, 2),
            skills_match_score=round(skill_match_score, 2),
            content_quality_score=round(content_quality_score, 2),
            resume_skills=resume_skills,
            missing_skills=missing_skills,
            matched_skills=matched_skills,
            sections_found=sections_found,
            grammar_errors=grammar_error_details,  # ← NOW HAS DETAILS!
            formatting_issues=formatting_issues,
            feedback=feedback,
            recommendations=recommendations,
            best_matching_job=job_match if job_match.get("found") else None
        )
    
    def generate_report(self, result: ResumeAnalysisResult) -> Dict[str, Any]:
        """Generate clean report from results"""
        return {
            'summary': {
                'overall_score': result.overall_score,
                'ats_compatibility': result.ats_score,
                'job_match': result.job_match_score,
                'skills_match': result.skills_match_score,
                'content_quality': result.content_quality_score
            },
            'skills_analysis': {
                'found': result.resume_skills,
                'missing': result.missing_skills,
                'matched': result.matched_skills,
                'match_percentage': result.skills_match_score
            },
            'grammar_details': result.grammar_errors[:5],  # Show first 5 errors
            'formatting_issues': result.formatting_issues,
            'feedback': result.feedback,
            'recommendations': result.recommendations
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
        "grammar_details": result.grammar_errors[:3]  # ← NOW SHOWS DETAILS!
    }