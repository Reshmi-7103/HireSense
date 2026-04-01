# utils/grammar_checker.py
"""
Purpose: Check grammar and spelling with detailed error locations
Output: Error count AND list of errors with context and suggestions
"""

import re
from typing import Tuple, List, Dict

def check_grammar(text: str, grammar_tool=None) -> Tuple[int, List[Dict[str, any]]]:
    """
    Check grammar and spelling errors with detailed context
    Returns: (error_count, list_of_errors_with_details)
    """
    if not grammar_tool:
        return 0, []
    
    try:
        matches = grammar_tool.check(text[:5000])
        errors = []
        
        for match in matches[:20]:  # Limit to 20 errors
            # Extract surrounding context (3 lines before/after)
            lines = text.split('\n')
            error_line = None
            line_number = 0
            context_lines = []
            
            # Find which line contains the error
            for i, line in enumerate(lines):
                if match.context in line or match.matched_text in line:
                    error_line = line.strip()
                    line_number = i + 1
                    # Get context: line before, error line, line after
                    start = max(0, i-1)
                    end = min(len(lines), i+2)
                    context_lines = lines[start:end]
                    break
            
            errors.append({
                'message': match.message,
                'context': match.context,
                'matched_text': match.matched_text,
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