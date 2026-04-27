"""
Similarity Module - Compares resume with a specific job role
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any, Optional


def compute_similarity(resume_text: str, job_description: str) -> float:
    """
    Compare resume with a single job description.
    
    Args:
        resume_text: Cleaned resume text
        job_description: Job description text
    
    Returns:
        Similarity score (0 to 1)
    """
    if not resume_text or not job_description:
        return 0.0
    
    corpus = [resume_text, job_description]
    
    vectorizer = TfidfVectorizer(
        stop_words="english",
        lowercase=True
    )
    
    tfidf_matrix = vectorizer.fit_transform(corpus)
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    
    return similarity[0][0]


def get_job_match_score(resume_text: str, job_row: Any) -> Dict[str, Any]:
    """
    Calculate match score between resume and a specific job.
    
    Args:
        resume_text: Cleaned resume text
        job_row: DataFrame row containing job_title, job_description, job_skill_set
    
    Returns:
        Dictionary with match score and job details
    """
    job_description = job_row.get("job_description", "")
    job_skills = str(job_row.get("job_skill_set", "")).split(",")
    job_skills = [s.strip().lower() for s in job_skills if s.strip()]
    
    similarity_score = compute_similarity(resume_text, job_description)
    
    return {
        "job_title": job_row.get("job_title", "Unknown"),
        "similarity_score": round(similarity_score * 100, 2),
        "job_skills": job_skills
    }