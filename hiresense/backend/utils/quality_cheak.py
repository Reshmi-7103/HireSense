# utils/quality_checker.py
"""
Purpose: Check content quality - action verbs, metrics, bullet points, length, and more
Output: Quality score and detailed suggestions
"""

import re
from typing import Tuple, List, Dict

# Action verbs list
ACTION_VERBS = [
    'achieved', 'improved', 'implemented', 'developed', 'managed', 'created',
    'led', 'increased', 'reduced', 'designed', 'built', 'optimized',
    'coordinated', 'spearheaded', 'transformed', 'accelerated', 'streamlined',
    'delivered', 'launched', 'executed', 'established', 'generated', 'produced',
    'initiated', 'pioneered', 'revolutionized', 'spearheaded', 'championed'
]


def check_content_quality(text: str, sections: Dict[str, str]) -> Tuple[float, List[str]]:
    """
    Check content quality and provide detailed suggestions
    Returns: (quality_score, suggestions)
    """
    suggestions = []
    score = 100
    
    # ========== 1. ACTION VERBS CHECK ==========
    exp_text = sections.get("experience", "").lower()
    proj_text = sections.get("projects", "").lower()
    all_experience = exp_text + proj_text
    
    if all_experience:
        found_verbs = [v for v in ACTION_VERBS if v in all_experience]
        if len(found_verbs) == 0:
            suggestions.append("⚡ Start bullet points with strong action verbs (developed, led, created, improved)")
            score -= 15
        elif len(found_verbs) < 3:
            suggestions.append(f"⚡ Use more action verbs. Found only {len(found_verbs)}. Try: developed, implemented, optimized")
            score -= 8
    
    # ========== 2. METRICS CHECK ==========
    metrics_pattern = r'\d+%|\d+\s*percent|\$\d+|\d+\s*times|\d+\+|increased by|decreased by|reduced by|improved by'
    has_metrics = re.search(metrics_pattern, all_experience)
    
    if not has_metrics:
        suggestions.append("📊 Add quantifiable achievements (e.g., 'improved performance by 30%', 'reduced costs by $10K')")
        score -= 15
    else:
        # Count metrics
        metrics_count = len(re.findall(r'\d+%|\$\d+|\d+\s*times', all_experience))
        if metrics_count < 2:
            suggestions.append(f"📊 Add more metrics. Found only {metrics_count}. Add numbers, percentages, or dollar amounts")
            score -= 5
    
    # ========== 3. BULLET POINTS CHECK ==========
    bullet_pattern = r'[•\-*•\d+\.]\s|▪|▫|✓|→|⟡'
    has_bullets = re.search(bullet_pattern, all_experience)
    
    if not has_bullets and len(all_experience) > 100:
        suggestions.append("📌 Use bullet points to format experience and projects (•, -, *, 1., etc.)")
        score -= 10
    
    # ========== 4. RESUME LENGTH CHECK ==========
    word_count = len(text.split())
    if word_count < 200:
        suggestions.append(f"📄 Resume is too short ({word_count} words). Add more details about projects and experience")
        score -= 10
    elif word_count > 1200:
        suggestions.append(f"📄 Resume is too long ({word_count} words). Aim for 400-800 words (1-2 pages)")
        score -= 10
    elif 300 < word_count < 600:
        suggestions.append(f"✅ Good resume length: {word_count} words")
        # No penalty
    
    # ========== 5. SECTIONS CHECK ==========
    missing_sections = []
    if not sections.get("summary"):
        missing_sections.append("Professional Summary")
    if not sections.get("experience") and not sections.get("projects"):
        missing_sections.append("Experience or Projects")
    if not sections.get("skills"):
        missing_sections.append("Skills")
    
    if missing_sections:
        suggestions.append(f"📁 Add missing sections: {', '.join(missing_sections)}")
        score -= len(missing_sections) * 10
    
    # ========== 6. CONTACT INFO CHECK ==========
    if '@' not in text:
        suggestions.append("📧 Add email address to contact section")
        score -= 10
    if not re.search(r'\d{10}|\d{3}[-.]?\d{3}[-.]?\d{4}', text):
        suggestions.append("📞 Add phone number to contact section")
        score -= 5
    
    # Check for LinkedIn/GitHub
    has_linkedin = 'linkedin' in text.lower()
    has_github = 'github' in text.lower()
    if not has_linkedin and not has_github:
        suggestions.append("🔗 Add LinkedIn and GitHub links to showcase your work")
        score -= 5
    
    # ========== 7. PASSIVE VOICE CHECK ==========
    passive_patterns = [
        r'was developed', r'were created', r'has been', r'have been',
        r'is used', r'are used', r'was implemented'
    ]
    passive_count = 0
    for pattern in passive_patterns:
        passive_count += len(re.findall(pattern, text.lower()))
    
    if passive_count > 3:
        suggestions.append(f"✍️ Reduce passive voice. Found {passive_count} instances. Use active voice (e.g., 'I developed' instead of 'was developed')")
        score -= 8
    elif passive_count > 0:
        suggestions.append(f"✍️ Found {passive_count} passive voice instances. Try using active voice for stronger impact")
        score -= 3
    
    # ========== 8. CONSISTENCY CHECK ==========
    # Check for inconsistent date formats
    date_formats = re.findall(r'\d{4}\s*[-–]\s*\d{4}|\d{4}\s*-\s*Present|\w+\s+\d{4}', text)
    if len(set(date_formats)) > 3 and len(date_formats) > 5:
        suggestions.append("📅 Use consistent date format throughout your resume (e.g., '2022-2026' or 'Jan 2022 - Present')")
        score -= 5
    
    # ========== 9. SKILLS SECTION CHECK ==========
    skills_text = sections.get("skills", "")
    skill_items = re.findall(r'[a-zA-Z+#\.]+', skills_text)
    unique_skills = set([s.lower() for s in skill_items if len(s) > 1])
    
    if len(unique_skills) < 8:
        suggestions.append(f"🎯 Expand skills section. Found {len(unique_skills)} skills. Aim for 10-15 relevant skills")
        score -= 8
    elif len(unique_skills) > 25:
        suggestions.append(f"🎯 Too many skills ({len(unique_skills)}). Focus on most relevant 15-20 skills")
        score -= 5
    
    # ========== 10. PROJECTS SECTION CHECK ==========
    proj_text = sections.get("projects", "")
    if proj_text:
        proj_count = proj_text.count('●') + proj_text.count('•') + proj_text.count('- ') + len(re.findall(r'\d+\.', proj_text))
        if proj_count == 0:
            proj_count = len(re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+.*:', proj_text))
        
        if proj_count < 2:
            suggestions.append("📁 Add 2-3 detailed projects with descriptions")
            score -= 10
        elif proj_count > 5:
            suggestions.append(f"📁 You have {proj_count} projects. Consider keeping top 3-4 most relevant ones")
            # No penalty
    
    # ========== FINAL SCORE ==========
    final_score = max(0, min(100, score))
    
    # Add congratulatory message if score is high
    if final_score >= 85:
        suggestions.insert(0, "🎉 Great quality resume! Minor improvements can make it excellent.")
    elif final_score >= 70:
        suggestions.insert(0, "👍 Good quality resume. Review the suggestions below to improve.")
    
    return final_score, suggestions[:10]  # Return top 10 suggestions