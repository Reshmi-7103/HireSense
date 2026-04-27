"""
Skill Extractor Module - Extracts technical skills from cleaned resume text
"""

import re
from typing import List, Set, Optional
import pandas as pd


def load_job_dataset(csv_path: str) -> Optional[pd.DataFrame]:
    """
    Load job dataset from CSV file.
    """
    try:
        df = pd.read_csv(csv_path)
        print(f"✅ Loaded {len(df)} jobs")
        return df
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return None


def build_global_skill_set(df: pd.DataFrame) -> Set[str]:
    """
    Build master set of all skills from all jobs.

    Takes CSV with 'job_skill_set' column containing comma-separated skills.
    Example: "python, java, MySQL" → {"python", "java", "MySQL"}
    """
    all_skills = set()

    if df is None or df.empty:
        return all_skills

    # Find skill column
    skill_col = None
    for col in ["job_skill_set", "skills", "required_skills"]:
        if col in df.columns:
            skill_col = col
            break

    if skill_col is None:
        print("⚠️ No skill column found in CSV")
        return all_skills

    # Extract skills from each job
    for skills_str in df[skill_col].dropna():
        if isinstance(skills_str, str):
            # Split by comma, clean, add to set
            for skill in skills_str.split(","):
                skill = skill.strip().lower()
                if skill and len(skill) > 1:
                    all_skills.add(skill)

    print(f"✅ Built global skills set: {len(all_skills)} unique skills")
    return all_skills


def extract_resume_skills(text: str, global_skills: Set[str]) -> List[str]:
    """
    Extract skills from resume text by matching against global skills set.

    How it works:
    1. Split text into words
    2. Check each word against global_skills
    3. Also check 2-word phrases (e.g., "machine learning")
    4. Return unique matched skills
    """
    if not text or not global_skills:
        return []

    text_lower = text.lower()

    # Method 1: Single word matching
    words = re.findall(r"[a-z0-9\+\.#]+", text_lower)

    # Method 2: Two-word phrases (for skills like "machine learning", "data science")
    two_word_phrases = []
    for i in range(len(words) - 1):
        phrase = f"{words[i]} {words[i+1]}"
        two_word_phrases.append(phrase)

    # Method 3: Three-word phrases (for skills like "object oriented programming")
    three_word_phrases = []
    for i in range(len(words) - 2):
        phrase = f"{words[i]} {words[i+1]} {words[i+2]}"
        three_word_phrases.append(phrase)

    # Check all candidates against global skills
    found_skills = set()

    # Check single words
    for word in words:
        if word in global_skills and len(word) > 1:
            found_skills.add(word)

    # Check two-word phrases
    for phrase in two_word_phrases:
        if phrase in global_skills:
            found_skills.add(phrase)

    # Check three-word phrases
    for phrase in three_word_phrases:
        if phrase in global_skills:
            found_skills.add(phrase)

    return sorted(list(found_skills))


def compute_skill_match_score(resume_skills: List[str], job_skills: List[str]) -> float:
    """
    Calculate percentage of job skills found in resume.

    Example:
        resume_skills = ['python', 'git']
        job_skills = ['python', 'java', 'MySQL']
        Returns: 33.33 (1 out of 3)
    """
    if not job_skills:
        return 0.0

    resume_set = set(s.lower() for s in resume_skills)
    job_set = set(s.lower() for s in job_skills)

    if not job_set:
        return 0.0

    matched = len(resume_set.intersection(job_set))
    return round((matched / len(job_set)) * 100, 2)


def get_skill_match_details(resume_skills: List[str], job_skills: List[str]) -> dict:
    """
    Get detailed skill match information.
    """
    resume_set = set(s.lower() for s in resume_skills)
    job_set = set(s.lower() for s in job_skills)

    return {
        "matched_skills": list(resume_set.intersection(job_set)),
        "missing_skills": list(job_set - resume_set),
        "match_percentage": compute_skill_match_score(resume_skills, job_skills),
        "total_required": len(job_set),
        "total_matched": len(resume_set.intersection(job_set)),
    }
