import re
import os
import pandas as pd
import pdfplumber
import docx
import requests
from dotenv import load_dotenv

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ─────────────────────────────────────────────
# 🔐 LOAD ENV
# ─────────────────────────────────────────────
load_dotenv()
API_KEY = os.getenv("RAPIDAPI_KEY")

# ─────────────────────────────────────────────
# 📂 LOAD CSV (fallback)
# ─────────────────────────────────────────────
CSV_PATH = os.path.join(os.path.dirname(__file__), "jobs.csv")


def load_jobs():
    try:
        df = pd.read_csv(CSV_PATH)
    except:
        print("⚠️ jobs.csv not found")
        return pd.DataFrame(
            columns=["job_title", "company_name", "location", "job_url", "text_data"]
        )

    # ✅ SAFE column handling
    if "job_description" not in df.columns:
        df["job_description"] = ""
    else:
        df["job_description"] = df["job_description"].fillna("")

    if "skills" not in df.columns:
        df["skills"] = ""
    else:
        df["skills"] = df["skills"].fillna("")

    df["job_title"] = df.get("job_title", "").fillna("")
    df["location"] = df.get("location", "").fillna("").str.lower()

    df["text_data"] = df["job_title"] + " " + df["job_description"] + " " + df["skills"]

    print(f"✅ Loaded {len(df)} jobs")
    return df


jobs_df = load_jobs()

# ─────────────────────────────────────────────
# 🎯 DOMAIN → ROLE MAP
# ─────────────────────────────────────────────
DOMAIN_TO_ROLE = {
    "tech": "software developer",
    "data": "data analyst",
    "engineering": "mechanical engineer",
    "marketing": "digital marketing",
    "hr": "human resources",
    "design": "ui ux designer",
}

DOMAIN_KEYWORDS = {
    "tech": ["python", "java", "react", "node", "flask", "django", "api"],
    "data": ["pandas", "numpy", "MySQL", "tableau"],
    "engineering": ["mechanical", "civil", "electrical"],
    "marketing": ["seo", "marketing", "branding"],
    "hr": ["recruitment", "hr"],
    "design": ["figma", "ui", "ux"],
}


# ─────────────────────────────────────────────
# 🌐 LIVE JOB FETCH (FIXED)
# ─────────────────────────────────────────────
def fetch_live_jobs(role, location="mumbai"):
    url = "https://jsearch.p.rapidapi.com/search"

    # 🔥 CLEAN QUERY (IMPORTANT FIX)
    querystring = {
        "query": role,  # only role (NOT sentence)
        "location": location,  # separate location
        "page": "1",
        "num_pages": "1",
        "country": "in",  # 🇮🇳 CRITICAL
        "date_posted": "month",  # recent jobs
    }

    headers = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": "jsearch.p.rapidapi.com"}

    jobs = []

    try:
        res = requests.get(url, headers=headers, params=querystring)

        print("🔍 API STATUS:", res.status_code)
        data = res.json()

        if "data" not in data:
            print("❌ No data key in API response")
            return pd.DataFrame()

        for job in data["data"]:
            jobs.append(
                {
                    "job_title": job.get("job_title", ""),
                    "company_name": job.get("employer_name", ""),
                    "location": (job.get("job_city") or location).lower(),
                    "job_url": job.get("job_apply_link", ""),
                    "text_data": (
                        job.get("job_title", "")
                        + " "
                        + (job.get("job_description") or "")
                    ),
                }
            )

        print(f"🌐 Live jobs fetched: {len(jobs)}")

    except Exception as e:
        print("❌ API Error:", e)

    return pd.DataFrame(jobs)


# ─────────────────────────────────────────────
# 🧠 DOMAIN DETECTION
# ─────────────────────────────────────────────
def detect_domain(text):
    text = text.lower()
    scores = {}

    for domain, keywords in DOMAIN_KEYWORDS.items():
        score = sum(2 if kw in text else 0 for kw in keywords)
        scores[domain] = score

    best = max(scores, key=scores.get)

    if scores[best] < 3:
        print("⚠️ Weak domain → using all")
        return "all"

    print(f"✅ Domain: {best}")
    return best


# ─────────────────────────────────────────────
# 📍 LOCATION DETECTION
# ─────────────────────────────────────────────
CITIES = ["mumbai", "delhi", "bangalore", "pune", "hyderabad", "chennai"]


def detect_location(text):
    text = text.lower()

    for city in CITIES:
        if city in text:
            print(f"📍 Location: {city}")
            return city

    print("📍 Default location: India")
    return "India"


# ─────────────────────────────────────────────
# 📄 RESUME PARSER
# ─────────────────────────────────────────────
def extract_resume_text(file_path):
    text = ""

    try:
        if file_path.endswith(".pdf"):
            with pdfplumber.open(file_path) as pdf:
                for p in pdf.pages:
                    text += p.extract_text() or ""

        elif file_path.endswith(".docx"):
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text

    except Exception as e:
        print("Resume error:", e)
        return ""

    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text)


# ─────────────────────────────────────────────
# 🚀 MAIN FUNCTION
# ─────────────────────────────────────────────
def recommend_jobs(file_path, top_n=10):

    resume_text = extract_resume_text(file_path)

    if not resume_text:
        return []

    print("\n📄 Resume preview:", resume_text[:200])

    # STEP 1
    domain = detect_domain(resume_text)
    location = detect_location(resume_text)

    # STEP 2
    df_local = jobs_df.copy()

    # STEP 3 → LIVE jobs
    role_query = DOMAIN_TO_ROLE.get(domain, "software developer")
    df_live = fetch_live_jobs(role_query, location)

    # STEP 4 → COMBINE
    combined_df = pd.concat([df_live, df_local], ignore_index=True)

    if combined_df.empty:
        return []

    # STEP 5 → TF-IDF
    corpus = combined_df["text_data"].tolist() + [resume_text]

    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(corpus)

    scores = cosine_similarity(matrix[-1], matrix[:-1]).flatten()

    top_n = min(top_n, len(scores))
    top_idx = scores.argsort()[::-1][:top_n]

    result = combined_df.iloc[top_idx][
        ["job_title", "company_name", "location", "job_url"]
    ].copy()

    result["match_score"] = (scores[top_idx] * 100).round(1)
    result["match_score"] = result["match_score"].replace(0, 5)

    print("\n✅ FINAL RESULTS:")
    for _, r in result.iterrows():
        print(f"{r['job_title']} → {r['match_score']}%")

    return result.to_dict(orient="records")
