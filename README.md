# HireSense

**Intelligent Support System for Job Seekers**

AI-powered platform for resume analysis, mock interviews, and job recommendations.

---

## Features

- **Resume Analyzer** - Upload resume, get ATS score, skills gap analysis, grammar check, and improvement suggestions
- **AI Mock Interview** - Practice technical and HR interviews with AI
- **Job Recommendations** - Personalized job suggestions based on resume
- **Admin Dashboard** - Manage users, monitor activity, resolve queries

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React.js, Vite, CSS |
| Backend | Python, Flask |
| Database | MongoDB |
| ML/NLP | spaCy, scikit-learn, language-tool-python |

---

## Project Structure

```
HireSense/
│
├── backend/
│   ├── app.py
│   ├── resume_analyzer.py
│   ├── job_recommender.py
│   ├── requirements.txt
│   ├── utils/
│   └── resumes/
│
├── client/
│   ├── src/
│   └── package.json
│
└── hiresense-admin/
    ├── src/
    └── package.json
```

---

## Installation

### Prerequisites
- Python 3.10 or higher
- Node.js 18 or higher
- MongoDB instance

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python app.py
```

### Client Setup

```bash
cd client
npm install
npm run dev
```

### Admin Setup

```bash
cd hiresense-admin
npm install
npm run dev
```

---

## Environment Variables

Create `.env` in `backend/` folder:

```
MONGO_URL=mongodb://localhost:27017/hiresense
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/register | User registration |
| POST | /api/login | User login |
| POST | /api/analyze-resume/<user_id> | Resume analysis |
| POST | /api/recommend-jobs/<user_id> | Job recommendations |
| POST | /api/interview/save | Save interview session |
| GET | /api/interview/list/<user_id> | Get interview history |
| POST | /api/admin-login | Admin login |
| GET | /api/admin-data | Dashboard data |


---

## Contributors

- Reshmi
- Krushnali
- Nandini

*Final Year Information Technology Students*

---

## Future Enhancements

- Resume version tracking and improvement history
- Interview performance analytics and feedback
- Job application tracking dashboard
- Email notifications for new job matches
- Export analysis reports as PDF

---

## License

This project is developed for educational purposes as part of the Final Year Information Technology program.

---

