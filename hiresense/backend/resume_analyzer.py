import re

from utils.pdf_parser import extract_text_from_pdf
from utils.text_cleaner import clean_text
from utils.skill_extracter import (
    load_job_dataset,
    build_global_skill_set,
    extract_resume_skills,
    compute_skill_match_score
)
from utils.similarity import compute_similarity


# ---------------- JOB DESCRIPTION ----------------
job_description = """
We are looking for a Data Analyst with strong skills in Python, SQL,
Power BI, data visualization, statistics, and machine learning basics.
Experience with projects and problem-solving is required.
"""


# ---------------- RESUME PIPELINE ----------------
resume_text = extract_text_from_pdf("uploads/Resume_Jagtap.pdf")
cleaned_resume = clean_text(resume_text)

cleaned_jd = clean_text(job_description)


# ---------------- SKILL VOCAB ----------------
df = load_job_dataset("data/all_job_post.csv")
global_skills = build_global_skill_set(df)


# ---------------- SKILL EXTRACTION ----------------
resume_skills = extract_resume_skills(cleaned_resume, global_skills)
jd_skills = extract_resume_skills(cleaned_jd, global_skills)

matched_skills = sorted(set(resume_skills) & set(jd_skills))
missing_skills = sorted(set(jd_skills) - set(resume_skills))


# ---------------- ALIGNMENT SCORE ----------------
alignment_score = compute_similarity(
    cleaned_resume,
    [cleaned_jd]
)[0] * 100


# ---------------- RULE BASED AUDITS ----------------
def check_sections(text):
    sections = ["experience", "projects", "education", "skills"]
    return {sec: sec in text.lower() for sec in sections}

def has_numbers(text):
    return len(re.findall(r'\d+', text)) > 0


sections = check_sections(resume_text)
feedback = []

if not sections["projects"]:
    feedback.append("Add a Projects section with 2–3 relevant projects.")

if missing_skills:
    feedback.append(
        f"Learn and showcase these missing skills: {', '.join(missing_skills[:5])}"
    )

if not has_numbers(cleaned_resume):
    feedback.append(
        "Add numbers to quantify impact (e.g., accuracy, users, datasets)."
    )


# ---------------- PROJECT SUGGESTIONS ----------------
PROJECT_SUGGESTIONS = {
    "powerbi": "Build a Power BI dashboard using sales or retail data",
    "sql": "Create a SQL-based data analysis project with joins and aggregations",
    "machine learning": "Implement a churn prediction or classification project"
}

project_ideas = [
    PROJECT_SUGGESTIONS[s]
    for s in missing_skills
    if s in PROJECT_SUGGESTIONS
]


# ---------------- OUTPUT (TEMP DEBUG) ----------------
print("\nAlignment Score:", round(alignment_score, 2), "%")
print("\nMatched Skills:", matched_skills)
print("\nMissing Skills:", missing_skills)
print("\nFeedback:")
for f in feedback:
    print("-", f)

print("\nSuggested Projects:")
for p in project_ideas:
    print("-", p)
