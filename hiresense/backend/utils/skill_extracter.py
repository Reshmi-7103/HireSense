# utils/skill_extracter.py

import pandas as pd
from typing import List, Set

def load_job_dataset(csv_path: str) -> pd.DataFrame:
    """
    WHAT IT DOES: Loads the CSV file containing job data
    WHY: We need job descriptions and skills to compare with resume
    RETURNS: Pandas DataFrame (table) with job data
    """
    return pd.read_csv(csv_path)

def build_global_skill_set(df: pd.DataFrame) -> Set[str]:
    """
    WHAT IT DOES: Creates a master list of ALL skills from ALL jobs
    WHY: We need to know what skills exist in the job market to extract them from resume
    HOW: 
        - Takes the job_skill_set column from CSV (contains skills like "Python, Java, SQL")
        - Splits each job's skills by comma
        - Adds all skills to a set (automatically removes duplicates)
    RETURNS: Set of unique skills (e.g., {"python", "java", "sql", "react", ...})
    """
    all_skills = set()
    
    # Check which column in CSV contains the skills
    if "job_skill_set" in df.columns:
        skill_column = "job_skill_set"  # Your CSV uses this column name
    else:
        # Try other possible column names (fallback)
        for col in ["skills", "required_skills", "cleaned_job_posts"]:
            if col in df.columns:
                skill_column = col
                break
        else:
            print("Warning: No skill column found. Available columns:", df.columns.tolist())
            return all_skills
    
    # Loop through each row in the skill column
    for skill_list in df[skill_column].dropna():  # dropna() removes empty rows
        if isinstance(skill_list, str):
            # Split "Python, Java, SQL" into ["python", "java", "sql"]
            skills = [s.strip().lower() for s in skill_list.split(",")]
            all_skills.update(skills)  # Add all skills to the set
    
    return all_skills

def extract_resume_skills(text: str, global_skills: Set[str]) -> List[str]:
    """
    WHAT IT DOES: Finds which skills from global set are present in resume
    WHY: To see what technical skills the candidate has
    HOW:
        - Takes resume text and global skills set
        - Converts both to lowercase
        - Checks each skill: if skill appears in resume text, add to list
    RETURNS: List of skills found in resume (e.g., ["python", "javascript", "react"])
    """
    found_skills = []
    text_lower = text.lower()  # Convert resume text to lowercase for matching
    
    # Check each skill from global set
    for skill in global_skills:
        if skill in text_lower:  # If skill word appears in resume
            found_skills.append(skill)
    
    return found_skills

def compute_skill_match_score(resume_skills: List[str], job_skills: List[str]) -> float:
    """
    WHAT IT DOES: Calculates what percentage of job-required skills the candidate has
    WHY: To quantify how well candidate's skills match the job requirements
    HOW:
        - Convert both lists to sets (for easier math)
        - Count overlapping skills (candidate has AND job requires)
        - Divide by total job skills needed
        - Multiply by 100 to get percentage
    EXAMPLE:
        Job needs: ["python", "java", "sql"]
        Candidate has: ["python", "javascript"]
        Match = (1 overlapping skill) / 3 total job skills = 33.33%
    RETURNS: Percentage score (0-100)
    """
    if not job_skills:
        return 0.0
    
    # Convert to lowercase sets for case-insensitive matching
    resume_set = set([s.lower() for s in resume_skills])
    job_set = set([s.lower() for s in job_skills])
    
    if not job_set:
        return 0.0
    
    # Count how many job skills the candidate has
    matched = len(resume_set.intersection(job_set))
    
    # Calculate percentage
    return (matched / len(job_set)) * 100