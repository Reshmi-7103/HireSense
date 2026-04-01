# utils/ats_checker.py
"""
Purpose: Check resume formatting for ATS compatibility
Output: Score (0-100) and list of issues
"""

import re
from typing import Tuple, List

def check_ats_compatibility(text: str) -> Tuple[float, List[str]]:
    """
    Check if resume is ATS-friendly
    Returns: (score, list_of_issues)
    """
    issues = []
    score = 100
    
    # Check for tables
    if '|' in text or '\t' in text:
        issues.append("Contains tables or tabular formatting which may confuse ATS")
        score -= 20
    
    # Check for unusual characters
    unusual_chars = re.findall(r'[^\x00-\x7F]+', text)
    if unusual_chars:
        issues.append("Contains special/unusual characters that may not parse correctly")
        score -= 15
    
    # Check for images/graphics
    if 'image' in text.lower() or 'graphic' in text.lower():
        issues.append("Contains images/graphics - ATS may skip these")
        score -= 15
    
    # Check contact info
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    
    if not re.search(email_pattern, text):
        issues.append("No email address found")
        score -= 10
    if not re.search(phone_pattern, text):
        issues.append("No phone number found")
        score -= 5
    
    # Check required sections (caller should provide sections)
    return max(0, score), issues