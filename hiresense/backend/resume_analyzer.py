import fitz
import language_tool_python
import requests

# ================= CONFIG ================= #
API_KEY = "YOUR_RAPIDAPI_KEY"   # ← add your key

# ================= GRAMMAR TOOL ================= #
try:
    tool = language_tool_python.LanguageTool('en-US')
except Exception as e:
    print(f"⚠️ LanguageTool disabled: {e}")
    tool = None


# ================= EXTRACT TEXT ================= #
def extract_text(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text.lower()


# ================= GRAMMAR CHECK ================= #
def grammar_check(text):
    if tool:
        matches = tool.check(text[:2000])   # limit for speed
    else:
        matches = []
    return min(len(matches), 15)


# ================= SKILL EXTRACTION ================= #
def extract_skills(text):

    skills_db = [
        "python","java","c++","react","html","css","javascript",
        "node","mongodb","sql","git","django","flask",
        "machine learning","deep learning","tensorflow","pytorch",
        "pandas","numpy","data analysis","data science",
        "docker","kubernetes","aws","linux","api","rest",
        "excel","power bi","tableau"
    ]

    text = text.replace("-", " ").replace(".", " ")

    return list(set([s for s in skills_db if s in text]))


# ================= ROLE SKILL MAP ================= #
role_skill_map = {
    "web developer":["html","css","javascript","react","node"],
    "frontend":["html","css","javascript","react"],
    "backend":["python","java","node","sql","api"],
    "data scientist":["python","machine learning","pandas","numpy"],
    "data analyst":["python","sql","excel","power bi"],
    "machine learning":["python","machine learning","tensorflow","pytorch"],
    "devops":["docker","kubernetes","aws","linux"]
}


# ================= ATS SCORE ================= #
def ats_score(skills, role):

    role = role.lower()
    required = []

    for key in role_skill_map:
        if key in role:
            required = role_skill_map[key]

    if not required:
        required = ["python","java","html","sql"]

    matched = sum(1 for s in required if s in skills)
    return round((matched / len(required)) * 100)


# ================= ROLE DETECTION ================= #
def detect_role(skills):

    if "machine learning" in skills or "tensorflow" in skills:
        return "Machine Learning Engineer"

    if "react" in skills:
        return "Frontend Developer"

    if "node" in skills:
        return "Backend Developer"

    if "sql" in skills and "python" in skills:
        return "Data Analyst"

    if "docker" in skills:
        return "DevOps Engineer"

    if "python" in skills:
        return "Python Developer"

    return "Software Engineer"


# ================= LIVE JOB FETCH ================= #
def fetch_live_jobs(role, location="India"):

    url = "https://jsearch.p.rapidapi.com/search"

    querystring = {
        "query": f"{role} jobs in {location}",
        "page": "1",
        "num_pages": "1"
    }

    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()

        jobs = []

        for job in data.get("data", [])[:10]:
            jobs.append({
                "job_title": job.get("job_title"),
                "company_name": job.get("employer_name"),
                "location": job.get("job_city") or "Remote",
                "job_url": job.get("job_apply_link"),
                "match_score": 90
            })

        return jobs

    except Exception as e:
        print("❌ API Error:", e)
        return []


# ================= ANALYZE RESUME ================= #
def analyze_resume(path, role_input=None):

    text = extract_text(path)

    grammar_errors = grammar_check(text)
    skills = extract_skills(text)

    # auto detect role if not provided
    role = role_input if role_input else detect_role(skills)

    score = ats_score(skills, role)

    # 🔥 LIVE JOBS
    print("🌐 Fetching LIVE jobs...")
    jobs = fetch_live_jobs(role)

    # match label
    if score > 70:
        match = "Strong Match"
    elif score > 40:
        match = "Moderate Match"
    else:
        match = "Weak Match"

    return {
        "skills": skills,
        "grammar_errors": grammar_errors,
        "ats_score": score,
        "role_detected": role,
        "role_match": match,
        "recommended_jobs": jobs   # 🔥 LIVE jobs
    }