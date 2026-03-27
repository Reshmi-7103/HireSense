from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS, cross_origin
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId
from resume_analyzer import analyze_resume
from job_recommender import recommend_jobs          # ← your ML module
import bcrypt
import datetime
import os

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

UPLOAD_FOLDER = "resumes"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

print("✅ MongoDB Connected Successfully")

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

# ─── RESUME ANALYSIS ──────────────────────────────────────────────────────────

@app.route("/api/analyze-resume/<user_id>", methods=["POST"])
@cross_origin()
def analyze_resume_api(user_id):
    try:
        role = request.form.get("role")
        if "resume" not in request.files:
            return jsonify({"success": False, "error": "No Resume Uploaded"}), 400

        file      = request.files["resume"]
        ext       = file.filename.split(".")[-1]
        filename  = f"{user_id}_analysis.{ext}"
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(save_path)

        result = analyze_resume(save_path, role)
        return jsonify({"success": True, "analysis": result})

    except Exception as e:
        print("ANALYSIS ERROR:", e)
        return jsonify({"success": False, "error": str(e)}), 500

# ─── RECOMMEND JOBS (ML) ──────────────────────────────────────────────────────
# POST  /api/recommend-jobs/<user_id>
# Body  : multipart/form-data  →  field "resume" (PDF / DOCX file)
# Returns: { success, jobs: [ { job_title, company_name, location, job_url, match_score } ] }

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

        # ── Call your ML model ──────────────────────────────────────────────
        jobs = recommend_jobs(save_path, top_n=10)
        # jobs is a list of dicts: job_title, company_name, location, job_url, match_score
        # ───────────────────────────────────────────────────────────────────

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