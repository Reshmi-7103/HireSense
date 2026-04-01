from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS, cross_origin
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId
import sys
import os
import datetime

# Add utils directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

# Import your modules
from resume_analyzer import ResumeAnalyzer
from job_recommender import recommend_jobs
import bcrypt
import json

# ─── Setup ────────────────────────────────────────────────────────────────────

load_dotenv()

app = Flask(__name__)
CORS(app)

MONGO_URL  = os.getenv("MONGO_URL")
client     = MongoClient(MONGO_URL)
db         = client["hiresense"]

users      = db["users"]
contacts   = db["contacts"]
activity   = db["activity"]
admins     = db["admin"]
interviews = db["interviews"]
resume_analyses = db["resume_analyses"]  # New collection for storing analysis results

UPLOAD_FOLDER = "resumes"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize resume analyzer
resume_analyzer = ResumeAnalyzer(job_data_path="D:\\HireSense 3.0\\HireSense\\hiresense\\backend\\utils\\cleaned_job_posts.csv")

print("✅ MongoDB Connected Successfully")
print("✅ Resume Analyzer Initialized")

# ─── REGISTER ─────────────────────────────────────────────────────────────────

@app.route("/api/register", methods=["POST", "OPTIONS"])
@cross_origin()
def register():
    try:
        data = request.json
        if users.find_one({"email": data["email"]}):
            return jsonify({"error": "User already exists"}), 400
        data["password"] = bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt())
        users.insert_one(data)
        return jsonify({"success": True})
    except Exception as e:
        print("REGISTER ERROR:", e)
        return jsonify({"error": "Server error"}), 500

# ─── LOGIN ────────────────────────────────────────────────────────────────────

@app.route("/api/login", methods=["POST", "OPTIONS"])
@cross_origin()
def login():
    try:
        data = request.json
        user = users.find_one({"email": data["email"]})
        if not user:
            return jsonify({"error": "User not found"}), 400
        if not bcrypt.checkpw(data["password"].encode(), user["password"]):
            return jsonify({"error": "Wrong password"}), 400

        clean_user = {
            "_id":        str(user["_id"]),
            "name":       user.get("name"),
            "email":      user.get("email"),
            "phone":      user.get("phone"),
            "college":    user.get("college"),
            "yop":        user.get("yop"),
            "dob":        user.get("dob"),
            "skills":     user.get("skills"),
            "experience": user.get("experience"),
            "resume":     user.get("resume"),
        }

        activity.insert_one({
            "user_id": str(user["_id"]),
            "email":   user.get("email"),
            "action":  "LOGIN"
        })

        return jsonify({"success": True, "user": clean_user})

    except Exception as e:
        print("LOGIN ERROR:", e)
        return jsonify({"error": "Server error"}), 500

# ─── LOGOUT ───────────────────────────────────────────────────────────────────

@app.route("/api/logout", methods=["POST", "OPTIONS"])
@cross_origin()
def logout():
    data = request.json
    activity.insert_one({"user_id": data.get("id"), "action": "LOGOUT"})
    return jsonify({"success": True})

# ─── CONTACT ──────────────────────────────────────────────────────────────────

@app.route("/api/contact", methods=["POST", "OPTIONS"])
@cross_origin()
def contact():
    try:
        data = request.json
        contacts.insert_one(data)
        return jsonify({"success": True})
    except Exception as e:
        print("CONTACT ERROR:", e)
        return jsonify({"error": "Server error"}), 500

# ─── UPDATE PROFILE ───────────────────────────────────────────────────────────

@app.route("/api/update-profile", methods=["PUT", "OPTIONS"])
@cross_origin()
def update_profile():
    try:
        data    = request.json
        user_id = data.get("id")
        if not user_id:
            return jsonify({"success": False, "error": "User ID missing"}), 400

        data.pop("id",  None)
        data.pop("_id", None)
        obj_id = ObjectId(str(user_id))

        result = users.update_one({"_id": obj_id}, {"$set": data})
        if result.matched_count == 0:
            return jsonify({"success": False, "error": "User not found"}), 404

        user = users.find_one({"_id": obj_id})
        user["_id"] = str(user["_id"])
        user.pop("password", None)
        return jsonify({"success": True, "user": user})

    except Exception as e:
        print("UPDATE ERROR:", e)
        return jsonify({"success": False, "error": "Server Error"}), 500

# ─── ADMIN LOGIN ──────────────────────────────────────────────────────────────

@app.route("/api/admin-login", methods=["POST", "OPTIONS"])
@cross_origin()
def admin_login():
    try:
        data  = request.json
        admin = admins.find_one({"email": data["email"]})
        if not admin:
            return jsonify({"error": "Admin not found"}), 400
        if not bcrypt.checkpw(data["password"].encode(), admin["password"].encode()):
            return jsonify({"error": "Wrong password"}), 400
        return jsonify({"success": True, "admin": {"email": admin["email"]}})
    except Exception as e:
        print("ADMIN LOGIN ERROR:", e)
        return jsonify({"error": "Server error"}), 500

# ─── ADMIN DASHBOARD DATA ─────────────────────────────────────────────────────

@app.route("/api/admin-data", methods=["GET"])
@cross_origin()
def admin_data():
    all_users    = list(users.find({}, {"password": 0}))
    all_contacts = list(contacts.find())
    all_activity = list(activity.find())

    for u in all_users:
        u["_id"] = str(u["_id"])
        u.setdefault("resume", None)
    for c in all_contacts:
        c["_id"] = str(c["_id"])
    for a in all_activity:
        a["_id"] = str(a["_id"])

    return jsonify({
        "total_users":  users.count_documents({}),
        "login_count":  activity.count_documents({"action": "LOGIN"}),
        "logout_count": activity.count_documents({"action": "LOGOUT"}),
        "users":        all_users,
        "contacts":     all_contacts,
        "activity":     all_activity,
    })

# ─── DELETE CONTACT QUERY ─────────────────────────────────────────────────────

@app.route("/api/delete-query", methods=["DELETE", "OPTIONS"])
@cross_origin()
def delete_query():
    if request.method == "OPTIONS":
        return jsonify({"success": True})
    try:
        obj_id = ObjectId(str(request.json.get("id")))
        result = contacts.delete_one({"_id": obj_id})
        if result.deleted_count == 0:
            return jsonify({"success": False, "error": "Query not found"}), 404
        return jsonify({"success": True})
    except Exception as e:
        print("DELETE ERROR:", e)
        return jsonify({"success": False, "error": "Server error"}), 500

# ─── UPLOAD RESUME ────────────────────────────────────────────────────────────

@app.route("/api/upload-resume/<user_id>", methods=["POST"])
@cross_origin()
def upload_resume(user_id):
    try:
        if "resume" not in request.files:
            return jsonify({"success": False, "error": "No file provided"}), 400

        file      = request.files["resume"]
        ext       = file.filename.split(".")[-1]
        filename  = f"{user_id}.{ext}"
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(save_path)

        obj_id = ObjectId(str(user_id))
        users.update_one({"_id": obj_id}, {"$set": {"resume": filename}})

        user = users.find_one({"_id": obj_id})
        user["_id"] = str(user["_id"])
        user.pop("password", None)

        return jsonify({"success": True, "user": user})

    except Exception as e:
        print("UPLOAD ERROR:", e)
        return jsonify({"success": False, "error": str(e)}), 500

# ─── GET RESUME FILE ──────────────────────────────────────────────────────────

@app.route("/resumes/<filename>")
def get_resume(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# ═══════════════════════════════════════════════════════════════════════════
# ║                    RESUME ANALYSIS SECTION (UPDATED)                     ║
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/api/analyze-resume/<user_id>", methods=["POST"])
@cross_origin()
def analyze_resume_api(user_id):
    """
    Comprehensive resume analysis with ATS scoring, keyword matching, and recommendations
    """
    try:
        if "resume" not in request.files:
            return jsonify({"success": False, "error": "No resume file provided"}), 400

        file = request.files["resume"]
        
        if file.filename == '':
            return jsonify({"success": False, "error": "No file selected"}), 400
        
        ext = file.filename.split(".")[-1].lower()
        if ext not in ["pdf", "docx"]:
            return jsonify({"success": False, "error": "Only PDF and DOCX files are supported"}), 400
        
        filename = f"{user_id}_analysis_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(save_path)
        
        job_description = request.form.get("job_description", None)
        required_skills = request.form.get("required_skills", None)
        
        if required_skills:
            try:
                required_skills = json.loads(required_skills)
            except:
                required_skills = [s.strip() for s in required_skills.split(",")]
        
        # Call analyzer with role parameter
        analysis_result = resume_analyzer.analyze_resume(
            file_path=save_path,
            role=job_description or required_skills
        )
        
        # Generate report
        report = resume_analyzer.generate_report(analysis_result)
        
        # Save to database - using correct attribute names from refactored analyzer
        analysis_record = {
            "user_id": user_id,
            "timestamp": datetime.datetime.now(datetime.timezone.utc),
            "filename": filename,
            "scores": {
                "ats_compatibility": analysis_result.ats_score,
                "job_match_score": analysis_result.job_match_score,
                "overall_score": analysis_result.overall_score
            },
            "skills_gap": {
                "match_percentage": analysis_result.skills_match_score,
                "matched_skills": analysis_result.matched_skills,
                "missing_skills": analysis_result.missing_skills
            },
            "report": report
        }
        
        resume_analyses.insert_one(analysis_record)
        
        # Clean up
        try:
            os.remove(save_path)
        except:
            pass
        
        # Return response with correct field names
        return jsonify({
            "success": True,
            "analysis": {
                "report": report,
                "scores": {
                    "ats_compatibility": analysis_result.ats_score,
                    "job_match_rate": analysis_result.job_match_score,
                    "ranking_score": analysis_result.overall_score
                },
                "skills_analysis": {
                    "matched_skills": analysis_result.matched_skills,
                    "missing_skills": analysis_result.missing_skills,
                    "match_percentage": analysis_result.skills_match_score
                },
                "content_issues": {
                    "grammar_errors": len(analysis_result.grammar_errors),
                    "grammar_details": analysis_result.grammar_errors[:3],  # Show first 3 errors with details
                    "formatting_issues": analysis_result.formatting_issues
                },
                "recommendations": analysis_result.recommendations[:5],
                "feedback": analysis_result.feedback
            }
        }), 200
        
    except Exception as e:
        print("ANALYSIS ERROR:", e)
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

# ─── RECOMMEND JOBS (ML) ──────────────────────────────────────────────────────

@app.route("/api/recommend-jobs/<user_id>", methods=["POST", "OPTIONS"])
@cross_origin()
def recommend_jobs_api(user_id):
    if request.method == "OPTIONS":
        return jsonify({"success": True})

    try:
        if "resume" not in request.files:
            return jsonify({"success": False, "error": "No resume file provided"}), 400

        file      = request.files["resume"]
        ext       = file.filename.split(".")[-1].lower()

        # Validate extension
        if ext not in ("pdf", "doc", "docx"):
            return jsonify({"success": False, "error": "Only PDF / DOCX supported"}), 400

        # Save temporarily for ML processing
        temp_filename = f"{user_id}_recommend.{ext}"
        save_path     = os.path.join(UPLOAD_FOLDER, temp_filename)
        file.save(save_path)

        # Call your ML model
        jobs = recommend_jobs(save_path, top_n=10)
        
        # Clean up
        try:
            os.remove(save_path)
        except:
            pass

        return jsonify({"success": True, "jobs": jobs})

    except Exception as e:
        print("RECOMMEND JOBS ERROR:", e)
        return jsonify({"success": False, "error": "Server error during job matching"}), 500

# ─── INTERVIEW: SAVE ──────────────────────────────────────────────────────────

@app.route("/api/interview/save", methods=["POST", "OPTIONS"])
@cross_origin()
def save_interview():
    try:
        data         = request.json
        user_id      = data.get("user_id")
        interview_id = data.get("interview_id")
        iv_type      = data.get("type")
        messages     = data.get("messages", [])
        timestamp    = data.get("timestamp", int(datetime.datetime.utcnow().timestamp() * 1000))

        if not user_id or not interview_id:
            return jsonify({"success": False, "error": "user_id and interview_id required"}), 400

        interviews.update_one(
            {"user_id": user_id, "interview_id": interview_id},
            {"$set": {
                "user_id":      user_id,
                "interview_id": interview_id,
                "type":         iv_type,
                "messages":     messages,
                "timestamp":    timestamp,
                "title":        f"{'Technical' if iv_type == 'technical' else 'HR'} Interview"
            }},
            upsert=True
        )
        return jsonify({"success": True})

    except Exception as e:
        print("SAVE INTERVIEW ERROR:", e)
        return jsonify({"success": False, "error": "Server error"}), 500

# ─── INTERVIEW: LIST ──────────────────────────────────────────────────────────

@app.route("/api/interview/list/<user_id>", methods=["GET", "OPTIONS"])
@cross_origin()
def list_interviews(user_id):
    try:
        docs = list(
            interviews.find({"user_id": user_id}, {"_id": 0}).sort("timestamp", -1)
        )
        return jsonify({"success": True, "interviews": docs})
    except Exception as e:
        print("LIST INTERVIEWS ERROR:", e)
        return jsonify({"success": False, "error": "Server error"}), 500

# ─── INTERVIEW: DELETE ────────────────────────────────────────────────────────

@app.route("/api/interview/delete", methods=["DELETE", "OPTIONS"])
@cross_origin()
def delete_interview():
    if request.method == "OPTIONS":
        return jsonify({"success": True})
    try:
        data         = request.json
        user_id      = data.get("user_id")
        interview_id = data.get("interview_id")

        if not user_id or not interview_id:
            return jsonify({"success": False, "error": "user_id and interview_id required"}), 400

        result = interviews.delete_one({"user_id": user_id, "interview_id": interview_id})

        if result.deleted_count == 0:
            return jsonify({"success": False, "error": "Interview not found"}), 404

        return jsonify({"success": True})

    except Exception as e:
        print("DELETE INTERVIEW ERROR:", e)
        return jsonify({"success": False, "error": "Server error"}), 500

# ─── HOME / HEALTH ────────────────────────────────────────────────────────────

@app.route("/")
def home():
    return "HireSense Backend Running 🚀"

# ─── RUN ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)