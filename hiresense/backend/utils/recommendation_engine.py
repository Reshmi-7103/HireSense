# utils/recommendation_engine.py
"""
Purpose: Generate specific, actionable recommendations
"""

import re
from typing import List, Dict

def generate_recommendations(
    missing_skills: List[str],
    sections: Dict[str, str],
    grammar_errors: List[Dict],
    text: str,
    action_verbs: List[str]
) -> List[str]:
    """
    Generate specific, actionable recommendations
    """
    recommendations = []
    
    # 1. Skill recommendations
    if missing_skills:
        top_missing = missing_skills[:5]
        recommendations.append(f"🎯 Add these missing skills: {', '.join(top_missing)}")
    
    # 2. Section recommendations
    if not sections.get("projects"):
        recommendations.append("📁 Create a projects section with 2-3 detailed project descriptions")
    
    if not sections.get("experience"):
        recommendations.append("💼 Add work experience or internship section")
    
    if not sections.get("summary"):
        recommendations.append("📌 Add a professional summary highlighting your key skills")
    
    # 3. Grammar recommendations (with examples)
    if grammar_errors:
        # Show specific grammar errors with context
        error_count = len(grammar_errors)
        if error_count > 10:
            recommendations.append(f"📝 Found {error_count} grammar issues. Here are the first few:")
            for err in grammar_errors[:3]:
                if err.get('line'):
                    recommendations.append(f"   • Line {err.get('line_number', '?')}: \"{err.get('line', '')[:60]}\" → {err.get('message', '')[:80]}")
        elif error_count > 0:
            recommendations.append(f"📝 Found {error_count} grammar issues. Review and fix them.")
    
    # 4. Action verb recommendations
    has_action_verbs = any(verb in text.lower() for verb in action_verbs[:10])
    if not has_action_verbs:
        recommendations.append("⚡ Start bullet points with strong action verbs: Developed, Built, Led, Optimized, Improved")
    
    # 5. Metrics recommendation
    has_metrics = bool(re.search(r'\d+%|\d+\s*percent|\$\d+|\d+\s*times|\d+\+', text))
    if not has_metrics:
        recommendations.append("📈 Add numbers! Use metrics like: 'increased sales by 30%', 'reduced time by 50%'")
    
    # 6. Links recommendation
    has_github = 'github.com' in text.lower() or 'github' in text.lower()
    has_linkedin = 'linkedin.com' in text.lower() or 'linkedin' in text.lower()
    
    if not has_github and not has_linkedin:
        recommendations.append("🔗 Add GitHub and LinkedIn links to showcase your work")
    elif not has_github:
        recommendations.append("🐙 Add GitHub profile link")
    elif not has_linkedin:
        recommendations.append("💼 Add LinkedIn profile link")
    
    return recommendations[:6]