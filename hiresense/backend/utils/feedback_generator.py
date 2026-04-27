# utils/feedback_generator.py
"""
Purpose: Generate human-readable feedback based on scores and analysis
"""

from typing import List, Dict


def generate_feedback(
    sections: Dict[str, str],
    resume_skills: List[str],
    skill_match_score: float,
    job_match_score: float,
    content_quality_score: float,
    missing_skills: List[str] = None,
    grammar_errors: int = 0,
    ats_score: float = None
) -> List[str]:
    """
    Generate actionable feedback based on analysis
    """
    feedback = []
    
    # ========== 1. SKILLS FEEDBACK ==========
    if len(resume_skills) < 5:
        feedback.append("📌 Add more technical skills (found only {len(resume_skills)}). Recruiters search for specific keywords.")
    elif len(resume_skills) < 10:
        feedback.append(f"📌 Good skill set with {len(resume_skills)} skills. Consider adding 2-3 more specialized skills.")
    else:
        feedback.append(f"✅ Great! Found {len(resume_skills)} relevant skills.")
    
    # Missing skills feedback
    if missing_skills and len(missing_skills) > 0:
        top_missing = missing_skills[:3]
        feedback.append(f"🎯 Add these key skills: {', '.join(top_missing)}")
    
    # ========== 2. SECTIONS FEEDBACK ==========
    if not sections.get("summary"):
        feedback.append("📌 Add a professional summary at the top (2-3 lines about your expertise and goals).")
    
    if not sections.get("experience"):
        feedback.append("💼 Add work experience or internship section. Include company name, role, dates, and achievements.")
    elif sections.get("experience") and len(sections.get("experience", "").split()) < 100:
        feedback.append("📊 Expand experience section. Add specific achievements, not just responsibilities.")
    
    if not sections.get("projects"):
        feedback.append("📁 Add a projects section. Showcase 2-3 projects with technologies used and your contributions.")
    elif len(sections.get("projects", "").split()) < 50:
        feedback.append("📝 Expand projects section. Add technologies used, your role, and measurable outcomes.")
    
    if not sections.get("education"):
        feedback.append("🎓 Add education section with degree, institution, and graduation year.")
    
    # ========== 3. ATS FEEDBACK ==========
    if ats_score:
        if ats_score < 50:
            feedback.append(f"⚠️ ATS score is low ({ats_score}%). Remove tables, columns, and special characters.")
        elif ats_score < 70:
            feedback.append(f"📄 ATS score is {ats_score}%. Improve by adding standard section headers (Experience, Education, Skills).")
        else:
            feedback.append(f"✅ Good ATS compatibility ({ats_score}%). Your resume is machine-readable.")
    
    # ========== 4. GRAMMAR FEEDBACK ==========
    if grammar_errors > 10:
        feedback.append(f"📝 Found {grammar_errors} grammar issues. Proofread carefully or use Grammarly.")
    elif grammar_errors > 3:
        feedback.append(f"✍️ Found {grammar_errors} grammar issues. Review punctuation and spelling.")
    elif grammar_errors > 0:
        feedback.append(f"✅ Only {grammar_errors} minor grammar issues. Good job!")
    
    # ========== 5. SCORE FEEDBACK ==========
    if skill_match_score < 30:
        feedback.append(f"🎯 Skills match is low ({skill_match_score}%). Add missing skills from job description.")
    elif skill_match_score < 60:
        feedback.append(f"🎯 Skills match is {skill_match_score}%. Good start, add {len(missing_skills) if missing_skills else 'few more'} relevant skills.")
    else:
        feedback.append(f"✅ Skills match is strong ({skill_match_score}%). Your skills align well with the role.")
    
    if job_match_score and job_match_score < 40:
        feedback.append("📄 Resume content doesn't match job description. Tailor your resume for each application.")
    
    if content_quality_score < 50:
        feedback.append("✨ Add metrics (30%, $10K, 5x) and action verbs (developed, led, created) to achievements.")
    elif content_quality_score < 75:
        feedback.append("📊 Good content quality. Add more numbers and metrics to strengthen achievements.")
    
    # ========== 6. RESUME LENGTH FEEDBACK ==========
    # (Will be passed from quality checker)
    
    # ========== 7. POSITIVE AFFIRMATION ==========
    if len(feedback) <= 2:
        feedback.insert(0, "🎉 Your resume looks great! Minor improvements below can make it excellent.")
    
    # Return top 6 most important feedback
    return feedback[:6]