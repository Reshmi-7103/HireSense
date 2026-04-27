# utils/grammar_checker.py
"""
Purpose: Check grammar and spelling with detailed error locations
Filters out false positives (names, emails, URLs, addresses, etc.)
"""

import re
from typing import Tuple, List, Dict


def check_grammar(text: str, grammar_tool=None) -> Tuple[int, List[Dict[str, any]]]:
    """
    Check grammar and spelling errors with detailed context
    Filters out false positives like all-caps names, emails, URLs, addresses
    
    Returns: (error_count, list_of_errors_with_details)
    """
    if not grammar_tool:
        return 0, []
    
    try:
        matches = grammar_tool.check(text[:5000])
        errors = []
        seen_errors = set()
        
        # List of city names to skip
        cities = ['mumbai', 'delhi', 'bangalore', 'pune', 'chennai', 'kolkata', 
                  'hyderabad', 'ahmedabad', 'jaipur', 'lucknow', 'nagpur',
                  'navi mumbai', 'kamothe', 'andheri', 'borivali', 'thane', 'malad']
        
        for match in matches[:30]:
            matched_text = match.matched_text if match.matched_text else ""
            message = match.message.lower()
            
            # ========== FILTER FALSE POSITIVES ==========
            
            # Skip whitespace warnings
            if 'whitespace' in message:
                continue
            
            # Skip all-caps words (proper names like "KRUSHNALI")
            if matched_text and matched_text.isupper() and len(matched_text) > 1:
                continue
            
            # Skip email addresses
            if '@' in matched_text:
                continue
            
            # Skip URLs
            if 'http' in matched_text or 'www' in matched_text or '.com' in matched_text:
                continue
            
            # Skip GitHub/LinkedIn
            if 'github' in matched_text.lower() or 'linkedin' in matched_text.lower():
                continue
            
            # Skip city/address names
            if matched_text.lower() in cities:
                continue
            
            # Skip single letters (except "I" as a word)
            if len(matched_text) == 1 and matched_text != 'I':
                continue
            
            # Skip pure numbers
            if matched_text and matched_text.isdigit():
                continue
            
            # Skip common tech terms
            tech_terms = ['reactjs', 'nodejs', 'mongodb', 'mysql', 'flask', 'numpy', 'pandas']
            if matched_text.lower() in tech_terms:
                continue
            
            # ========== FIND LINE NUMBER ==========
            
            lines = text.split('\n')
            error_line = None
            line_number = 0
            context_lines = []
            
            for i, line in enumerate(lines):
                if match.context in line or matched_text in line:
                    error_line = line.strip()
                    line_number = i + 1
                    start = max(0, i-1)
                    end = min(len(lines), i+2)
                    context_lines = lines[start:end]
                    break
            
            # Avoid duplicates
            error_key = f"{line_number}:{match.message[:50]}"
            if error_key in seen_errors:
                continue
            seen_errors.add(error_key)
            
            # ========== CATEGORIZE ERROR ==========
            
            category = "Spelling"
            if "grammar" in message or "verb" in message:
                category = "Grammar"
            elif "punctuation" in message or "period" in message or "full stop" in message:
                category = "Punctuation"
            elif "capital" in message:
                category = "Capitalization"
            elif "style" in message or "informal" in message:
                category = "Style"
            
            # ========== BUILD ERROR DETAILS ==========
            
            errors.append({
                'message': match.message,
                'category': category,
                'matched_text': matched_text,
                'line_number': line_number,
                'line': error_line,
                'context_lines': context_lines,
                'replacements': match.replacements[:3] if match.replacements else [],
                'rule_id': match.ruleId if hasattr(match, 'ruleId') else 'unknown'
            })
        
        return len(errors), errors
    
    except Exception as e:
        print(f"Grammar check error: {e}")
        return 0, []


def get_grammar_summary(errors: List[Dict]) -> Dict[str, int]:
    """
    Get summary of grammar errors by category
    """
    summary = {
        "total": len(errors),
        "spelling": 0,
        "grammar": 0,
        "punctuation": 0,
        "capitalization": 0,
        "style": 0
    }
    
    for error in errors:
        category = error.get('category', 'Spelling')
        if category == 'Spelling':
            summary['spelling'] += 1
        elif category == 'Grammar':
            summary['grammar'] += 1
        elif category == 'Punctuation':
            summary['punctuation'] += 1
        elif category == 'Capitalization':
            summary['capitalization'] += 1
        elif category == 'Style':
            summary['style'] += 1
    
    return summary


def format_errors_for_frontend(errors: List[Dict], max_errors: int = 5) -> List[Dict]:
    """
    Format errors for frontend display (limited number, cleaner format)
    """
    formatted = []
    
    for error in errors[:max_errors]:
        formatted.append({
            'line': error.get('line_number', '?'),
            'text': error.get('matched_text', ''),
            'message': error.get('message', ''),
            'category': error.get('category', 'Spelling'),
            'suggestion': error.get('replacements', [])[0] if error.get('replacements') else None
        })
    
    return formatted