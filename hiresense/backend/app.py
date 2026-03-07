from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import bcrypt
from werkzeug.utils import secure_filename
from flask import send_from_directory
from bson import ObjectId
from resume_analyzer import analyze_resume

# Load env
load_dotenv()

app = Flask(__name__)
CORS(app)

# MongoDB Connection
MONGO_URL = os.getenv("MONGO_URL")
client = MongoClient(MONGO_URL)

db = client["hiresense"]
users = db["users"]
contacts = db["contacts"]
activity = db["activity"]
admins = db["admin"]

print("✅ MongoDB Connected Successfully")

# 🔥 RESUME UPLOAD FOLDER
UPLOAD_FOLDER = "resumes"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ---------------- REGISTER ---------------- #

@app.route("/api/register", methods=["POST","OPTIONS"])
@cross_origin()
def register():
    try:
        data = request.json

        if users.find_one({"email": data["email"]}):
            return jsonify({"error": "User already exists"}), 400

        hashed = bcrypt.hashpw(
            data["password"].encode("utf-8"),
            bcrypt.gensalt()
        )

        data["password"] = hashed
        users.insert_one(data)

        return jsonify({"success": True})

    except Exception as e:
        print("REGISTER ERROR:", e)
        return jsonify({"error": "Server error"}), 500

# ---------------- LOGIN ---------------- #

@app.route("/api/login", methods=["POST","OPTIONS"])
@cross_origin()
def login():
    try:
        data = request.json
        user = users.find_one({"email": data["email"]})

        if not user:
            return jsonify({"error": "User not found"}), 400

        if not bcrypt.checkpw(
            data["password"].encode("utf-8"),
            user["password"]
        ):
            return jsonify({"error": "Wrong password"}), 400

        clean_user = {
            "_id": str(user["_id"]),
            "name": user.get("name"),
            "email": user.get("email"),
            "phone": user.get("phone"),
            "college": user.get("college"),
            "yop": user.get("yop"),
            "dob": user.get("dob"),
            "skills": user.get("skills"),
            "experience": user.get("experience"),
            "resume": user.get("resume")   # 🔥 ADDED
        }

        activity.insert_one({
            "user_id": str(user["_id"]),
            "email": user.get("email"),
            "action": "LOGIN"
        })

        return jsonify({
            "success": True,
            "user": clean_user
        })

    except Exception as e:
        print("LOGIN ERROR:", e)
        return jsonify({"error": "Server error"}), 500

# ---------------- LOGOUT ---------------- #

@app.route("/api/logout", methods=["POST","OPTIONS"])
@cross_origin()
def logout():
    data = request.json
    user_id = data.get("id")

    activity.insert_one({
        "user_id": user_id,
        "action": "LOGOUT"
    })

    return jsonify({"success": True})

# ---------------- CONTACT ---------------- #

@app.route("/api/contact", methods=["POST","OPTIONS"])
@cross_origin()
def contact():
    try:
        data = request.json
        print("CONTACT RECEIVED:", data)

        contacts.insert_one(data)

        return jsonify({"success": True})

    except Exception as e:
        print("CONTACT ERROR:", e)
        return jsonify({"error": "Server error"}), 500

# ---------------- UPDATE PROFILE ---------------- #

@app.route("/api/update-profile", methods=["PUT","OPTIONS"])
@cross_origin()
def update_profile():
    try:
        data = request.json
        user_id = data.get("id")

        if not user_id:
            return jsonify({
                "success": False,
                "error": "User ID missing"
            }), 400

        data.pop("id", None)
        data.pop("_id", None)

        obj_id = ObjectId(str(user_id))

        result = users.update_one(
            {"_id": obj_id},
            {"$set": data}
        )

        if result.matched_count == 0:
            return jsonify({
                "success": False,
                "error": "User not found"
            }), 404

        user = users.find_one({"_id": obj_id})

        if user:
            user["_id"] = str(user["_id"])
            user.pop("password", None)

        return jsonify({
            "success": True,
            "user": user
        })

    except Exception as e:
        print("UPDATE ERROR:", e)
        return jsonify({
            "success": False,
            "error": "Server Error"
        }), 500

# ---------------- ADMIN LOGIN ---------------- #

@app.route("/api/admin-login", methods=["POST","OPTIONS"])
@cross_origin()
def admin_login():
    try:
        data = request.json
        admin = admins.find_one({"email": data["email"]})

        if not admin:
            return jsonify({"error":"Admin not found"}),400

        if not bcrypt.checkpw(
            data["password"].encode("utf-8"),
            admin["password"].encode("utf-8")
        ):
            return jsonify({"error":"Wrong password"}),400

        return jsonify({
            "success":True,
            "admin":{
                "email":admin["email"]
            }
        })

    except Exception as e:
        print("ADMIN LOGIN ERROR:",e)
        return jsonify({"error":"Server error"}),500

# ---------------- ADMIN DASHBOARD DATA ---------------- #

@app.route("/api/admin-data", methods=["GET"])
@cross_origin()
def admin_data():

    total_users = users.count_documents({})
    login_count = activity.count_documents({"action":"LOGIN"})
    logout_count = activity.count_documents({"action":"LOGOUT"})

    all_users = list(users.find({},{
    "password":0
}))

    all_contacts = list(contacts.find())
    all_activity = list(activity.find())

    for u in all_users:
        u["_id"] = str(u["_id"])
        if "resume" not in u:
            u["resume"] = None

    for c in all_contacts:
        c["_id"] = str(c["_id"])

    for a in all_activity:
        a["_id"] = str(a["_id"])

    return jsonify({
        "total_users": total_users,
        "login_count": login_count,
        "logout_count": logout_count,
        "users": all_users,
        "contacts": all_contacts,
        "activity": all_activity
    })

# ---------------- DELETE CONTACT QUERY ---------------- #

@app.route("/api/delete-query", methods=["DELETE","OPTIONS"])
@cross_origin()
def delete_query():

    if request.method == "OPTIONS":
        return jsonify({"success": True})

    try:
        data = request.json
        query_id = data.get("id")

        obj_id = ObjectId(str(query_id))

        result = contacts.delete_one({"_id": obj_id})

        if result.deleted_count == 0:
            return jsonify({
                "success": False,
                "error": "Query not found"
            }),404

        return jsonify({"success": True})

    except Exception as e:
        print("DELETE ERROR:",e)
        return jsonify({
            "success": False,
            "error": "Server error"
        }),500

# ---------------- UPLOAD RESUME ---------------- #

@app.route("/api/upload-resume/<user_id>", methods=["POST"])
@cross_origin()
def upload_resume(user_id):

    try:
        if "resume" not in request.files:
            return jsonify({"success":False})

        file = request.files["resume"]

        # 🔥 IMPORTANT FIX (NO OVERWRITE)
        ext = file.filename.split(".")[-1]
        filename = f"{user_id}.{ext}"

        save_path = os.path.join(UPLOAD_FOLDER,filename)
        file.save(save_path)

        obj_id = ObjectId(str(user_id))

        users.update_one(
            {"_id":obj_id},
            {"$set":{"resume":filename}}
        )

        user = users.find_one({"_id":obj_id})
        user["_id"] = str(user["_id"])
        user.pop("password",None)

        return jsonify({
            "success":True,
            "user":user
        })

    except Exception as e:
        print("UPLOAD ERROR:",e)
        return jsonify({"success":False})

# ---------------- GET RESUME ---------------- #

@app.route("/resumes/<filename>")
def get_resume(filename):
    return send_from_directory(
        UPLOAD_FOLDER,
        filename
    )

# ---------------- RESUME ANALYSIS ---------------- #

@app.route("/api/analyze-resume/<user_id>", methods=["POST"])
@cross_origin()
def analyze_resume_api(user_id):

    try:

        role = request.form.get("role")

        if "resume" not in request.files:
            return jsonify({
                "success": False,
                "error": "No Resume Uploaded"
            })

        file = request.files["resume"]

        ext = file.filename.split(".")[-1]
        filename = f"{user_id}_analysis.{ext}"
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(save_path)

        # 🔥 CALL ANALYZER FUNCTION
        from resume_analyzer import analyze_resume
        result = analyze_resume(save_path, role)

        return jsonify({
            "success": True,
            "analysis": result
        })

    except Exception as e:
        print("ANALYSIS ERROR:", e)
        return jsonify({
            "success": False
        })

# ---------------- TEST ---------------- #

@app.route("/")
def home():
    return "HireSense Backend Running 🚀"

# ---------------- RUN ---------------- #

if __name__ == "__main__":
    app.run(debug=True)