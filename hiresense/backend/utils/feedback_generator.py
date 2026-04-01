# utils/feedback_generator.py
"""
Purpose: Generate human-readable feedback based on scores
"""

from typing import List, Dict

def generate_feedback(
    sections: Dict[str, str],
    resume_skills: List[str],
    skill_match_score: float,
    job_match_score: float,
    content_quality_score: float
) -> List[str]:
    """
    Generate actionable feedback based on analysis
    """
    feedback = []
    
    # Skill feedback
    if len(resume_skills) < 5:
        feedback.append("📌 Add more technical skills - recruiters search for specific keywords")
    elif len(resume_skills) < 10:
        feedback.append("📌 Good skill set! Consider adding 2-3 more specialized skills")
    
    # Section feedback
    if not sections.get("projects"):
        feedback.append("📁 Add a projects section - employers want to see practical work")
    elif len(sections.get("projects", "").split()) < 50:
        feedback.append("📝 Expand projects section with technologies used and your specific role")
    
    if not sections.get("experience"):
        feedback.append("💼 Add work experience or internship section")
    elif sections.get("experience") and len(sections.get("experience", "").split()) < 100:
        feedback.append("📊 Add more details to experience - what did you achieve?")
    
    if not sections.get("summary"):
        feedback.append("📌 Add a professional summary at the top")
    
    # Score feedback
    if skill_match_score < 40:
        feedback.append("🎯 Skills don't match job requirements - highlight relevant skills")
    
    if job_match_score < 50:
        feedback.append("📄 Resume content needs tailoring for target role")
    
    if content_quality_score < 70:
        feedback.append("✨ Add metrics and action verbs to make achievements stand out")
    
    return feedback[:5]