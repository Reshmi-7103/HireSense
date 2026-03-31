import pandas as pd
import re


# ---------------- LOAD JOB DATA ----------------
def load_job_dataset(csv_path):
    return pd.read_csv(csv_path)


# ---------------- BUILD GLOBAL SKILL SET ----------------
def build_global_skill_set(df):
    skills = set()

    for skill_list in df["job_skill_set"].dropna():
        for skill in str(skill_list).split(","):
            cleaned = normalize_text(skill)
            if len(cleaned) > 2:
                skills.add(cleaned)

    return sorted(skills)


# ---------------- NORMALIZATION ----------------
def normalize_text(text):
    text = text.lower()
    text = text.replace("&", "and")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ---------------- SKILL EXTRACTION (IMPORTANT) ----------------
def extract_resume_skills(text, global_skills):
    found_skills = set()
    text = normalize_text(text)
    tokens = set(text.split())

    for skill in global_skills:
        skill = normalize_text(skill)
        skill_tokens = skill.split()

        # Full phrase match
        if skill in text:
            found_skills.add(skill)

        # Partial token match (e.g. "data analysis")
        elif all(tok in tokens for tok in skill_tokens):
            found_skills.add(skill)

    return sorted(found_skills)


# ---------------- SKILL MATCH SCORE ----------------
def compute_skill_match_score(resume_skills, jd_skills):
    if not jd_skills:
        return 0.0

    matched = set(resume_skills) & set(jd_skills)
    score = (len(matched) / len(jd_skills)) * 100
    return round(score, 2)
