# utils/quality_checker.py
"""
Purpose: Check content quality - action verbs, metrics, bullet points, length
Output: Quality score and suggestions
"""

import re
from typing import Tuple, List, Dict

# Action verbs list
ACTION_VERBS = [
    'achieved', 'improved', 'implemented', 'developed', 'managed', 'created',
    'led', 'increased', 'reduced', 'designed', 'built', 'optimized',
    'coordinated', 'spearheaded', 'transformed', 'accelerated', 'streamlined',
    'delivered', 'launched', 'executed', 'established', 'generated', 'produced'
]

def check_content_quality(text: str, sections: Dict[str, str]) -> Tuple[float, List[str]]:
    """
    Check content quality and provide suggestions
    Returns: (quality_score, suggestions)
    """
    suggestions = []
    score = 100
    
    # Check for action verbs in experience section
    exp_text = sections.get("experience", "").lower()
    if exp_text:
        has_action_verbs = any(verb in exp_text for verb in ACTION_VERBS)
        if not has_action_verbs:
            suggestions.append("Use action verbs (developed, led, created) in experience section")
            score -= 15
    
    # Check for metrics (numbers/percentages)
    metrics_pattern = r'\d+%|\d+\s*percent|\$\d+|\d+\s*times|\d+\+'
    if not re.search(metrics_pattern, exp_text):
        suggestions.append("Add quantifiable achievements (e.g., 'improved performance by 30%')")
        score -= 15
    
    # Check bullet point structure
    bullet_pattern = r'[•\-*•\d+\.]\s'
    if not re.search(bullet_pattern, exp_text):
        suggestions.append("Use bullet points to format experience section")
        score -= 10
    
    # Check resume length
    word_count = len(text.split())
    if word_count < 200:
        suggestions.append("Resume is too short - add more details")
        score -= 10
    elif word_count > 1200:
        suggestions.append("Resume is too long - aim for 1-2 pages")
        score -= 10
    
    # Check contact info
    if '@' not in text:
        suggestions.append("Add email address")
        score -= 10
    if not re.search(r'\d{10}|\d{3}[-.]?\d{3}[-.]?\d{4}', text):
        suggestions.append("Add phone number")
        score -= 5
    
    return max(0, score), suggestions