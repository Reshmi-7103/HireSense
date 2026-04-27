"""
Text Cleaner Module - Optimized for Resume Parsing
Three-stage pipeline: Noise Removal → Entity Recognition Preparation → Standardization
"""

import re
import spacy
from typing import List, Dict, Tuple, Optional

# Load spaCy model (lazy loading)
_nlp = None

def _get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm")
    return _nlp


# ============================================================================
# STAGE 1: NOISE REMOVAL
# ============================================================================

def remove_noise(text: str) -> str:
    """
    Remove Unicode bullets, extra spaces, and formatting noise.
    
    Example: "●​ Python" → "Python"
             "Web \nDevelopment:" → "Web Development:"
    """
    if not text:
        return ""
    
    # Remove Unicode bullets and special characters
    text = re.sub(r'[●▪▸►•○■□▶❖→]', ' ', text)
    text = re.sub(r'[\u200b\u200c\u200d\u2060]', '', text)  # Zero-width spaces
    
    # Replace newlines with spaces (but keep section boundaries)
    text = text.replace('\n', ' ')
    text = text.replace('\t', ' ')
    text = text.replace('\r', ' ')
    
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing spaces
    text = text.strip()
    
    return text


def fix_broken_words(text: str) -> str:
    """
    Fix words broken across lines.
    
    Example: "Web \nDevelopment" → "Web Development"
             "ReactJS," → "ReactJS" (remove trailing comma space)
    """
    # Join words broken by newline (already replaced with space)
    # Fix common patterns like "ReactJS," → "ReactJS"
    text = re.sub(r',\s+', ', ', text)
    
    # Remove spaces before punctuation
    text = re.sub(r'\s+([.,;:!?)])', r'\1', text)
    
    return text


# ============================================================================
# STAGE 2: ENTITY RECOGNITION PREPARATION
# ============================================================================

def extract_candidate_name(text: str) -> Optional[str]:
    """
    Extract candidate name using spaCy NER and heuristics.
    
    Strategy:
    1. Look for PERSON entities at beginning of resume
    2. Fallback: First line that contains 2-4 words, no numbers, no special chars
    """
    if not text:
        return None
    
    nlp = _get_nlp()
    doc = nlp(text[:500])  # Check first 500 chars
    
    # Method 1: spaCy NER
    for ent in doc.ents:
        if ent.label_ == "PERSON" and 2 <= len(ent.text.split()) <= 4:
            # Verify it's likely a name (contains letters only)
            if re.match(r'^[A-Za-z\s\.]+$', ent.text):
                return ent.text.strip()
    
    # Method 2: Heuristic - First line that looks like a name
    lines = text.split('\n')[:5]
    for line in lines:
        line = line.strip()
        if line and len(line.split()) <= 4:
            # No numbers, no email, no special chars, not all caps
            if not re.search(r'\d|@|www|http', line):
                if not line.isupper():
                    return line
    
    return None


def detect_sections(text: str) -> Dict[str, str]:
    """
    Identify and extract resume sections.
    
    Returns:
        Dictionary with section names as keys and content as values
    """
    sections = {
        "summary": "",
        "skills": "",
        "experience": "",
        "education": "",
        "projects": "",
        "certifications": ""
    }
    
    text_lower = text.lower()
    
    # Section keywords mapping
    section_keywords = {
        "skills": ["technical skills", "skills", "core competencies", "technologies"],
        "experience": ["experience", "work experience", "employment", "internship"],
        "education": ["education", "academic", "qualifications"],
        "projects": ["projects", "project", "personal projects", "academic projects"],
        "summary": ["summary", "profile", "objective", "about me"],
        "certifications": ["certificate", "certification", "training", "courses"]
    }
    
    for section, keywords in section_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                # Find section start
                start = text_lower.find(keyword)
                # Find next section start
                end = len(text)
                for other_section in section_keywords:
                    for other_keyword in section_keywords[other_section]:
                        pos = text_lower.find(other_keyword, start + len(keyword))
                        if pos > start and pos < end:
                            end = pos
                sections[section] = text[start:end].strip()
                break
    
    return sections


# ============================================================================
# STAGE 3: STANDARDIZATION
# ============================================================================

def normalize_skill_text(text: str) -> str:
    """
    Standardize skill section for better extraction.
    
    Example: "Programming Languages: Java, Python" → "Java Python"
             "●​ Web Development: HTML, CSS" → "HTML CSS"
    """
    if not text:
        return ""
    
    # Remove section headers
    text = re.sub(r'(?i)(technical skills|skills|core competencies|technologies)', '', text)
    
    # Remove category labels (Programming Languages:, Web Development:, etc.)
    text = re.sub(r'[A-Za-z\s]+:', '', text)
    
    # Remove bullets and special chars
    text = re.sub(r'[●▪▸►•○■□▶❖→]', ' ', text)
    
    # Keep alphanumeric, spaces, basic punctuation
    text = re.sub(r'[^a-zA-Z0-9\s\+\.#]', ' ', text)
    
    # Normalize spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Split by comma and space, then rejoin
    items = re.split(r'[,|]', text)
    items = [item.strip() for item in items if item.strip()]
    
    return " ".join(items)


def clean_for_similarity(text: str) -> str:
    """
    Clean text for TF-IDF similarity matching.
    Removes stopwords, keeps important terms.
    """
    if not text:
        return ""
    
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    
    nlp = _get_nlp()
    doc = nlp(text)
    
    # Keep nouns, proper nouns, adjectives (important for similarity)
    important_words = [
        token.text for token in doc 
        if not token.is_stop 
        and len(token.text) > 2
        and token.pos_ in ['NOUN', 'PROPN', 'ADJ']
    ]
    
    return " ".join(important_words)


# ============================================================================
# MAIN CLEAN FUNCTION
# ============================================================================

def clean_text(text: str, extract_name: bool = False) -> str:
    """
    Main text cleaning function.
    
    Args:
        text: Raw extracted text from PDF
        extract_name: If True, also extract candidate name
        
    Returns:
        Cleaned text ready for skill extraction
    """
    if not text:
        return ""
    
    # Stage 1: Noise removal
    text = remove_noise(text)
    text = fix_broken_words(text)
    
    # Stage 2: Section detection (if needed)
    # (Sections are extracted separately in resume_analyzer.py)
    
    # Stage 3: Standardization for skill extraction
    text = normalize_skill_text(text)
    
    return text


# ============================================================================
# SPECIALIZED CLEANING FUNCTIONS
# ============================================================================

def clean_text_for_skill_extraction(text: str) -> str:
    """
    Specialized cleaning for skill extraction.
    Preserves technical terms, removes noise.
    """
    if not text:
        return ""
    
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s\+\.#\-]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def clean_text_basic(text: str) -> str:
    """
    Basic cleaning without NLP (faster, for quick operations).
    """
    if not text:
        return ""
    
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


# ============================================================================
# CANDIDATE INFO EXTRACTION
# ============================================================================

def extract_candidate_info(text: str) -> Dict[str, Optional[str]]:
    """
    Extract candidate name, email, phone from cleaned text.
    
    Returns:
        Dictionary with name, email, phone fields
    """
    info = {
        "name": None,
        "email": None,
        "phone": None
    }
    
    # Extract email
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    if emails:
        info["email"] = emails[0]
    
    # Extract phone (Indian format)
    phone_pattern = r'(\+91[\-\s]?)?[6-9]\d{9}'
    phones = re.findall(phone_pattern, text)
    if phones:
        info["phone"] = phones[0] if isinstance(phones[0], str) else phones[0][0]
    
    # Extract name (after cleaning)
    info["name"] = extract_candidate_name(text)
    
    return info


# For direct import
def clean_text(text: str) -> str:
    """
    Simple clean - just lowercase and remove extra spaces.
    Preserves ALL content.
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Replace newlines with spaces
    text = text.replace('\n', ' ').replace('\r', ' ')
    
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special bullets but keep words
    text = re.sub(r'[●▪▸►•○■□▶❖→]', '', text)
    
    return text.strip()