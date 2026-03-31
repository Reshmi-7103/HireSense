import fitz  # PyMuPDF

def analyze_resume(file_path, role=None):
    try:
        doc = fitz.open(file_path)
        text = ""

        for page in doc:
            text += page.get_text()

        text_lower = text.lower()

        score = 0
        feedback = []
        skills_found = []

        # Basic skills list
        skills = ["python", "java", "react", "mongodb", "sql", "html", "css"]

        for skill in skills:
            if skill in text_lower:
                skills_found.append(skill)
                score += 10

        # Basic checks
        if "project" not in text_lower:
            feedback.append("Add projects section")

        if "experience" not in text_lower:
            feedback.append("Add experience/internship")

        if len(skills_found) < 3:
            feedback.append("Add more technical skills")

        return {
            "score": min(score, 100),
            "skills": skills_found,
            "feedback": feedback
        }

    except Exception as e:
        return {"error": str(e)}