"""
PDF Parser Module - For simple straight resumes (single column, no complex layouts)
"""

import fitz  # PyMuPDF
import os
from typing import Optional


def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
    """
    Extract text from simple straight PDF resumes.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Extracted text as string, or None if extraction fails
    """
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return None
    
    if not pdf_path.lower().endswith('.pdf'):
        print(f"Not a PDF: {pdf_path}")
        return None
    
    try:
        doc = fitz.open(pdf_path)
        all_text = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            if text:
                all_text.append(text)
        
        doc.close()
        
        full_text = "\n".join(all_text)
        
        if not full_text.strip():
            return None
        
        return full_text
        
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return None