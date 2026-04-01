# HireSense 🚀

**Intelligent Support System for Job Seekers**

HireSense is an AI-powered web platform designed to help job seekers improve their employability through intelligent tools including resume analysis, mock interview preparation, and personalized job recommendations.

---

## Overview

The platform bridges the gap between job seekers and career opportunities by providing data-driven insights and interactive preparation tools. It features a user-facing application for job seekers and a dedicated admin dashboard for platform management.

---

## Key Features

### Resume Analyzer 📄
Upload resumes in PDF or DOCX format and receive comprehensive analysis including:
- ATS compatibility scoring
- Skills gap analysis
- Keyword matching against job descriptions
- Grammar and formatting issue detection
- Actionable improvement recommendations

### AI Mock Interview Preparation 🤖
Practice interview skills with AI-powered simulations:
- Technical interview preparation
- HR interview practice
- Real-time conversational interaction
- Interview history tracking

### Job Recommendation System 💼
Receive personalized job recommendations based on:
- Resume content analysis
- Skills matching
- Job role preferences

### Admin Dashboard
Manage platform operations with:
- User management and activity monitoring
- Resume review access
- Query handling and resolution
- Platform analytics

---

## Technology Stack 🧑‍💻 

| Layer | Technology |
|-------|------------|
| Frontend | React.js, Vite, CSS |
| Backend | Python, Flask |
| Database | MongoDB |
| ML/NLP | spaCy, scikit-learn, language-tool-python |

---

## Project Structure 📂
HireSense/
│
├── backend/ # Flask API server
│ ├── app.py # Main application
│ ├── resume_analyzer.py # Resume analysis logic
│ ├── job_recommender.py # Job matching
│ ├── requirements.txt
│ ├── utils/ # Utility modules
│ └── resumes/ # Uploaded files
│
├── client/ # User React app
│ ├── src/
│ └── package.json
│
└── hiresense-admin/ # Admin React app
├── src/
└── package.json


---

## Installation

### Prerequisites
- Python 3.10 or higher
- Node.js 18 or higher
- MongoDB instance

### Client Setup

cd client
npm install
npm run dev

### Backend Setup

```bash
- cd backend
- python -m venv venv
- source venv/bin/activate      # On Windows: venv\Scripts\activate
- pip install -r requirements.txt
- python -m spacy download en_core_web_sm
- python app.py

### Author
- Reshmi Krushnali Nandini Final Year Information Technology Student

### Future Enhancements

- Resume version tracking and improvement history
- Interview performance analytics and feedback
- Job application tracking dashboard
- Email notifications for new job matches
- Export analysis reports as PDF

### License
- This project is developed for educational purposes as part of the Final Year Information Technology program.
