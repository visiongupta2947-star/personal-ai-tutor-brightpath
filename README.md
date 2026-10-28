# AI-Powered Personal Tutor (Free Demo)

A beginner-friendly demo built with React + Vite, Python Flask, and SQLite.
It uses rule-based explanations and quiz questions, so no paid AI API key is needed.
This is a demo tutor, not a real large language model.

## Requirements
- Python 3.10+
- Node.js 18+ (includes npm)
- VS Code

## 1. Open the project
Extract the ZIP, then open the `ai_personal_tutor` folder in VS Code.

## 2. Start the Flask backend
Open a VS Code terminal (Terminal > New Terminal).

Windows PowerShell:
```powershell
cd backend
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

If PowerShell blocks activation, use Command Prompt terminal instead:
```bat
cd backend
py -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
python app.py
```

Backend runs at http://127.0.0.1:5000. Keep this terminal open.
SQLite database `tutor.db` is created automatically.

## 3. Start the React frontend
Open a SECOND terminal in VS Code:
```powershell
cd frontend
npm install
npm run dev
```
Open the URL printed by Vite, usually http://localhost:5173.

## How to use
1. Enter your name.
2. Choose a subject and click Start diagnostic.
3. Answer each question and submit.
4. Review your score and identified learning gaps.
5. Open the personalized lesson and take the practice quiz.
6. Your sessions and answers are saved in SQLite.

## Project structure
- `backend/app.py`: Flask routes, quiz logic, gap analysis, lessons, SQLite persistence.
- `backend/requirements.txt`: Python dependencies.
- `frontend/package.json`: JavaScript dependencies and scripts.
- `frontend/index.html`: React page entry point.
- `frontend/src/main.jsx`: React entry point.
- `frontend/src/App.jsx`: UI and user flow.
- `frontend/src/styles.css`: styling.

## Troubleshooting
- `py` not recognized: install Python from python.org and enable "Add Python to PATH", then reopen VS Code.
- `npm` not recognized: install Node.js LTS, then reopen VS Code.
- Port 5000 in use: close the other app using it, or change `port=5000` in `backend/app.py` and `API` in `frontend/src/App.jsx` to the same new port.
- CORS/network error: make sure Flask is running in the first terminal.
- To reset demo history, stop Flask and delete `backend/tutor.db`; it will be recreated next time.
