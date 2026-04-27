# utils/recommendation_engine.py
"""
Purpose: Generate specific, actionable recommendations based on analysis
"""

import re
from typing import List, Dict


def generate_recommendations(
    missing_skills: List[str],
    sections: Dict[str, str],
    grammar_errors: List[Dict],
    text: str,
    action_verbs: List[str],
    ats_score: float = None,
    skill_match_score: float = None
) -> List[str]:
    """
    Generate specific, actionable recommendations
    """
    recommendations = []
    
    # ========== 1. SKILL RECOMMENDATIONS ==========
    if missing_skills:
        top_missing = missing_skills[:5]
        if len(missing_skills) <= 3:
            recommendations.append(f"🎯 Add these missing skills: {', '.join(top_missing)}")
        else:
            recommendations.append(f"🎯 Focus on adding these key skills first: {', '.join(top_missing)}")
            recommendations.append(f"📚 Also consider: {', '.join(missing_skills[3:6])}...")
    
    # ========== 2. SECTION RECOMMENDATIONS (with priority) ==========
    missing_sections = []
    if not sections.get("summary"):
        missing_sections.append("Summary")
    if not sections.get("experience"):
        missing_sections.append("Experience")
    if not sections.get("projects"):
        missing_sections.append("Projects")
    if not sections.get("skills"):
        missing_sections.append("Skills")
    
    if missing_sections:
        recommendations.append(f"📁 Add missing sections: {', '.join(missing_sections)}")
        
        # Section-specific tips
        if "Summary" in missing_sections:
            recommendations.append("   • Summary: 2-3 lines about your expertise and career goals")
        if "Experience" in missing_sections:
            recommendations.append("   • Experience: Include company name, role, dates, and 3-4 bullet points")
        if "Projects" in missing_sections:
            recommendations.append("   • Projects: List 2-3 projects with technologies used and your role")
    
    # ========== 3. ATS RECOMMENDATIONS ==========
    if ats_score and ats_score < 60:
        recommendations.append("📄 Improve ATS compatibility:")
        if ats_score < 40:
            recommendations.append("   • Remove tables, columns, and special characters")
        recommendations.append("   • Use standard section headers: 'Experience', 'Education', 'Skills'")
        recommendations.append("   • Save as .pdf or .docx format")
    
    # ========== 4. GRAMMAR RECOMMENDATIONS ==========
    if grammar_errors:
        error_count = len(grammar_errors)
        if error_count > 10:
            recommendations.append(f"📝 Fix {error_count} grammar issues. Top issues:")
            for i, err in enumerate(grammar_errors[:3]):
                line_info = f"Line {err.get('line_number', '?')}" if err.get('line_number') else "Near"
                error_text = err.get('matched_text', '')[:30]
                suggestions = err.get('replacements', [])
                if suggestions:
                    recommendations.append(f"   • {line_info}: '{error_text}' → Suggested: '{suggestions[0]}'")
                else:
                    recommendations.append(f"   • {line_info}: {err.get('message', '')[:60]}")
        elif error_count > 0:
            recommendations.append(f"📝 Review {error_count} grammar issues. Use a spell checker for quick fixes.")
    
    # ========== 5. ACTION VERB RECOMMENDATIONS ==========
    exp_text = sections.get("experience", "") + sections.get("projects", "")
    has_action_verbs = any(verb in exp_text.lower() for verb in action_verbs[:15])
    
    if not has_action_verbs:
        recommendations.append("⚡ Start bullet points with strong action verbs:")
        recommendations.append(f"   • Examples: {', '.join(action_verbs[:8])}")
    else:
        # Count action verbs used
        found_verbs = [v for v in action_verbs if v in exp_text.lower()]
        if len(found_verbs) < 3:
            recommendations.append(f"⚡ Use more varied action verbs. Found only {len(found_verbs)}. Try: created, implemented, optimized")
    
    # ========== 6. METRICS RECOMMENDATIONS ==========
    metrics_pattern = r'\d+%|\d+\s*percent|\$\d+|\d+\s*times|\d+\+|increased by|decreased by|reduced by'
    has_metrics = bool(re.search(metrics_pattern, exp_text))
    
    if not has_metrics:
        recommendations.append("📈 Add measurable achievements with numbers:")
        recommendations.append("   • 'Improved performance by 30%'")
        recommendations.append("   • 'Reduced costs by $10,000'")
        recommendations.append("   • 'Increased user engagement by 2x'")
    else:
        # Count metrics
        metrics_count = len(re.findall(r'\d+%|\$\d+|\d+\s*times', exp_text))
        if metrics_count < 2:
            recommendations.append(f"📈 Add more metrics. Found only {metrics_count}. Aim for 3-4 quantifiable achievements per role.")
    
    # ========== 7. LINKS RECOMMENDATIONS ==========
    has_github = 'github.com' in text.lower() or 'github' in text.lower()
    has_linkedin = 'linkedin.com' in text.lower() or 'linkedin' in text.lower()
    has_portfolio = 'portfolio' in text.lower()
    
    missing_links = []
    if not has_github:
        missing_links.append("GitHub")
    if not has_linkedin:
        missing_links.append("LinkedIn")
    if not has_portfolio:
        missing_links.append("Portfolio")
    
    if missing_links:
        recommendations.append(f"🔗 Add {', '.join(missing_links)} links to showcase your work")
    
    # ========== 8. SKILL MATCH RECOMMENDATIONS (if score provided) ==========
    if skill_match_score and skill_match_score < 50:
        recommendations.append(f"🎯 Skills match is {skill_match_score}%. Tailor resume for each job:")
        recommendations.append("   • Use keywords from job description")
        recommendations.append("   • Highlight most relevant skills first")
    
    # ========== 9. RESUME LENGTH RECOMMENDATION ==========
    word_count = len(text.split())
    if word_count < 200:
        recommendations.append(f"📄 Resume is short ({word_count} words). Add more details about projects and achievements.")
    elif word_count > 1000:
        recommendations.append(f"📄 Resume is long ({word_count} words). Aim for 400-800 words (1-2 pages).")
    
    # ========== 10. POSITIVE AFFIRMATION ==========
    if len(recommendations) <= 3:
        recommendations.insert(0, "🎉 Your resume is in good shape! Minor improvements below can make it excellent.")
    
    # Remove duplicates and return top 8
    seen = set()
    unique_recs = []
    for rec in recommendations:
        if rec not in seen:
            seen.add(rec)
            unique_recs.append(rec)
    
    return unique_recs[:8]