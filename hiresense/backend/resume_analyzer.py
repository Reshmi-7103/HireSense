import fitz
import language_tool_python

# grammar tool
tool = language_tool_python.LanguageTool('en-US')


# ---------------- EXTRACT TEXT ---------------- #

def extract_text(file_path):

    doc = fitz.open(file_path)
    text = ""

    for page in doc:
        text += page.get_text()

    return text.lower()


# ---------------- GRAMMAR CHECK ---------------- #

def grammar_check(text):

    # check limited text (resume formatting causes false errors)
    matches = tool.check(text[:800])

    # limit grammar errors to realistic value
    return min(len(matches), 15)


# ---------------- SKILL EXTRACTION ---------------- #

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

    found = []

    for skill in skills_db:
        if skill in text:
            found.append(skill)

    return list(set(found))


# ---------------- ROLE SKILLS MAP ---------------- #

role_skill_map = {

    "web developer":[
        "html","css","javascript","react","node"
    ],

    "frontend":[
        "html","css","javascript","react"
    ],

    "backend":[
        "python","java","node","sql","api"
    ],

    "data scientist":[
        "python","machine learning","pandas","numpy"
    ],

    "data analyst":[
        "python","sql","excel","power bi"
    ],

    "machine learning":[
        "python","machine learning","tensorflow","pytorch"
    ],

    "devops":[
        "docker","kubernetes","aws","linux"
    ]

}


# ---------------- ATS SCORE ---------------- #

def ats_score(skills, role):

    role = role.lower()

    required = []

    for key in role_skill_map:
        if key in role:
            required = role_skill_map[key]

    # if role unknown
    if len(required) == 0:
        required = ["python","java","html","sql"]

    matched = 0

    for skill in required:
        if skill in skills:
            matched += 1

    score = (matched / len(required)) * 100

    return round(score)


# ---------------- JOB RECOMMENDATION ---------------- #

def recommend_jobs(skills, role):

    role = role.lower()

    jobs = []

    if "web" in role:
        jobs += ["Frontend Developer","Full Stack Developer"]

    if "data" in role:
        jobs += ["Data Scientist","Data Analyst"]

    if "machine learning" in role or "ai" in role:
        jobs += ["Machine Learning Engineer"]

    if "devops" in role:
        jobs += ["DevOps Engineer"]

    # skill based

    if "react" in skills:
        jobs.append("React Developer")

    if "java" in skills:
        jobs.append("Java Developer")

    if "python" in skills:
        jobs.append("Python Developer")

    if "sql" in skills:
        jobs.append("Database Developer")

    return list(set(jobs))


# ---------------- ANALYZE RESUME ---------------- #

def analyze_resume(path, role):

    text = extract_text(path)

    grammar_errors = grammar_check(text)

    skills = extract_skills(text)

    score = ats_score(skills, role)

    jobs = recommend_jobs(skills, role)

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
        "role_match": match,
        "recommended_jobs": jobs

    }