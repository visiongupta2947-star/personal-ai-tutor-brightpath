from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
CORS(app)

DB_PATH = Path(__file__).with_name("tutor.db")

# Small offline question bank. This demo does not call a paid AI service.
QUESTION_BANK = {
    "Python": [
        {"id": "py1", "topic": "variables", "question": "Which line stores 10 in a variable named age?",
         "options": ["age = 10", "10 = age", "age == 10", "store(age, 10)"], "answer": 0,
         "explanation": "Use = to assign a value: age = 10."},
        {"id": "py2", "topic": "loops", "question": "Which loop is commonly used to go through each item in a list?",
         "options": ["if", "for", "def", "return"], "answer": 1,
         "explanation": "A for loop visits items in a sequence one at a time."},
        {"id": "py3", "topic": "conditions", "question": "Which keyword starts a conditional branch in Python?",
         "options": ["repeat", "when", "if", "check"], "answer": 2,
         "explanation": "The if keyword runs a block when its condition is true."},
        {"id": "py4", "topic": "functions", "question": "Which keyword defines a function in Python?",
         "options": ["func", "define", "function", "def"], "answer": 3,
         "explanation": "Python functions are declared with def, for example: def greet():"},
        {"id": "py5", "topic": "lists", "question": "What is the index of the first item in a Python list?",
         "options": ["1", "-1", "0", "It has no index"], "answer": 2,
         "explanation": "Python lists use zero-based indexing, so the first item is at index 0."}
    ],
    "Math": [
        {"id": "ma1", "topic": "addition", "question": "What is 7 + 5?",
         "options": ["11", "12", "13", "35"], "answer": 1,
         "explanation": "Adding 7 and 5 gives 12."},
        {"id": "ma2", "topic": "multiplication", "question": "What is 6 × 4?",
         "options": ["10", "20", "24", "64"], "answer": 2,
         "explanation": "Six groups of four make 24."},
        {"id": "ma3", "topic": "fractions", "question": "Which fraction is equal to one half?",
         "options": ["2/3", "2/4", "3/4", "1/3"], "answer": 1,
         "explanation": "2/4 simplifies to 1/2 by dividing numerator and denominator by 2."},
        {"id": "ma4", "topic": "algebra", "question": "If x + 3 = 8, what is x?",
         "options": ["3", "5", "8", "11"], "answer": 1,
         "explanation": "Subtract 3 from both sides: x = 8 - 3 = 5."},
        {"id": "ma5", "topic": "division", "question": "What is 20 ÷ 5?",
         "options": ["2", "4", "5", "15"], "answer": 1,
         "explanation": "20 divided into 5 equal groups gives 4 in each group."}
    ],
    "Science": [
        {"id": "sc1", "topic": "plants", "question": "Which part of most plants absorbs water from the soil?",
         "options": ["Flower", "Root", "Fruit", "Leaf tip"], "answer": 1,
         "explanation": "Roots absorb water and minerals from the soil."},
        {"id": "sc2", "topic": "solar system", "question": "Which planet is known as the Red Planet?",
         "options": ["Venus", "Jupiter", "Mars", "Mercury"], "answer": 2,
         "explanation": "Iron-rich dust gives Mars its reddish appearance."},
        {"id": "sc3", "topic": "matter", "question": "Which state of matter has a fixed shape and fixed volume?",
         "options": ["Gas", "Liquid", "Solid", "Plasma only"], "answer": 2,
         "explanation": "A solid generally keeps both its shape and its volume."},
        {"id": "sc4", "topic": "human body", "question": "Which organ pumps blood around the human body?",
         "options": ["Lungs", "Heart", "Stomach", "Kidney"], "answer": 1,
         "explanation": "The heart contracts to pump blood through the circulatory system."},
        {"id": "sc5", "topic": "energy", "question": "What is the main natural source of energy for Earth's climate system?",
         "options": ["The Moon", "The Sun", "Volcanoes", "Ocean tides"], "answer": 1,
         "explanation": "Solar energy from the Sun drives most weather and climate processes."}
    ]
}

LESSONS = {
    "Python": {
        "variables": ("Variables", "A variable is a name that refers to a value. Example: age = 10. The equals sign assigns the value on the right to the name on the left."),
        "loops": ("Loops", "A loop repeats work. A for loop can visit every item: for fruit in fruits: print(fruit). Indentation shows which lines belong to the loop."),
        "conditions": ("Conditions", "An if statement makes a decision: if age >= 18: print('Adult'). The indented code runs only when the condition is true."),
        "functions": ("Functions", "A function is reusable code. Define it with def, such as def greet(): followed by an indented body. Call it with greet()."),
        "lists": ("Lists", "A list stores multiple values, such as colours = ['red', 'blue']. Python starts counting list positions at index 0.")
    },
    "Math": {
        "addition": ("Addition", "Addition combines quantities. Break a sum into easy parts: 7 + 5 = 7 + 3 + 2 = 12."),
        "multiplication": ("Multiplication", "Multiplication is repeated addition. 6 × 4 means six groups of four, or 4 + 4 + 4 + 4 + 4 + 4 = 24."),
        "fractions": ("Fractions", "A fraction represents part of a whole. Equivalent fractions name the same amount. For example, multiply both 1 and 2 by 2 to get 2/4 = 1/2."),
        "algebra": ("Simple algebra", "Keep an equation balanced by doing the same operation on both sides. If x + 3 = 8, subtract 3 from each side to get x = 5."),
        "division": ("Division", "Division splits a quantity into equal groups. 20 ÷ 5 asks how many are in each of five equal groups: 4.")
    },
    "Science": {
        "plants": ("Plant roots", "Roots anchor a plant and absorb water and minerals from the soil. Water then travels through the plant to support its functions."),
        "solar system": ("The Red Planet", "Mars is called the Red Planet because iron-rich dust on its surface gives it a reddish colour."),
        "matter": ("States of matter", "A solid generally has a fixed shape and volume. A liquid has a fixed volume but takes the shape of its container; a gas expands to fill its container."),
        "human body": ("The heart", "The heart is a muscular organ that pumps blood. Blood carries oxygen and nutrients to tissues and helps transport waste products."),
        "energy": ("The Sun and Earth", "Energy from the Sun drives most of Earth's weather and climate. The surface absorbs sunlight and releases energy back as heat.")
    }
}

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            subject TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            gaps TEXT NOT NULL,
            created_at TEXT NOT NULL
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            question_id TEXT NOT NULL,
            selected_index INTEGER NOT NULL,
            is_correct INTEGER NOT NULL,
            FOREIGN KEY(session_id) REFERENCES sessions(id)
        )""")

def public_question(q):
    return {"id": q["id"], "topic": q["topic"], "question": q["question"], "options": q["options"]}

@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "message": "Personal Tutor API is running"})

@app.get("/api/subjects")
def subjects():
    return jsonify({"subjects": list(QUESTION_BANK.keys())})

@app.get("/api/diagnostic")
def diagnostic():
    subject = request.args.get("subject", "Python")
    if subject not in QUESTION_BANK:
        return jsonify({"error": "Unknown subject"}), 400
    return jsonify({"subject": subject, "questions": [public_question(q) for q in QUESTION_BANK[subject]]})

@app.post("/api/submit")
def submit():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "Student").strip()[:80] or "Student"
    subject = data.get("subject", "Python")
    answers = data.get("answers", {})
    if subject not in QUESTION_BANK:
        return jsonify({"error": "Unknown subject"}), 400

    questions = QUESTION_BANK[subject]
    score = 0
    gap_counts = {}
    answer_rows = []
    review = []
    for q in questions:
        try:
            selected = int(answers.get(q["id"], -1))
        except (TypeError, ValueError):
            selected = -1
        correct = selected == q["answer"]
        score += int(correct)
        if not correct:
            gap_counts[q["topic"]] = gap_counts.get(q["topic"], 0) + 1
        answer_rows.append((q["id"], selected, int(correct)))
        review.append({
            "id": q["id"], "topic": q["topic"], "question": q["question"],
            "selected_index": selected, "correct_index": q["answer"],
            "is_correct": correct, "explanation": q["explanation"]
        })

    gaps = sorted(gap_counts, key=gap_counts.get, reverse=True)
    now = datetime.now().isoformat(timespec="seconds")
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO sessions(student_name, subject, score, total, gaps, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (name, subject, score, len(questions), ", ".join(gaps), now)
        )
        session_id = cur.lastrowid
        conn.executemany(
            "INSERT INTO answers(session_id, question_id, selected_index, is_correct) VALUES (?, ?, ?, ?)",
            [(session_id, qid, selected, correct) for qid, selected, correct in answer_rows]
        )

    percent = round(score / len(questions) * 100)
    lesson_topics = gaps if gaps else [questions[0]["topic"]]
    return jsonify({
        "session_id": session_id, "name": name, "subject": subject,
        "score": score, "total": len(questions), "percent": percent,
        "gaps": gaps, "lesson_topics": lesson_topics, "review": review,
        "message": "Great work! Review your learning gaps and practice again." if gaps else "Excellent! You answered every question correctly."
    })

@app.get("/api/lesson")
def lesson():
    subject = request.args.get("subject", "Python")
    topic = request.args.get("topic", "")
    if subject not in LESSONS:
        return jsonify({"error": "Unknown subject"}), 400
    if topic not in LESSONS[subject]:
        topic = next(iter(LESSONS[subject]))
    title, content = LESSONS[subject][topic]
    return jsonify({"subject": subject, "topic": topic, "title": title, "content": content,
                    "note": "This lesson is selected from the built-in demo lesson library."})

@app.get("/api/history")
def history():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, student_name, subject, score, total, gaps, created_at FROM sessions ORDER BY id DESC LIMIT 10"
        ).fetchall()
    return jsonify({"history": [dict(r) for r in rows]})

@app.post("/api/practice")
def practice():
    data = request.get_json(silent=True) or {}
    subject = data.get("subject", "Python")
    topic = data.get("topic", "")
    if subject not in QUESTION_BANK:
        return jsonify({"error": "Unknown subject"}), 400
    questions = [q for q in QUESTION_BANK[subject] if not topic or q["topic"] == topic]
    if not questions:
        questions = QUESTION_BANK[subject]
    return jsonify({"questions": [public_question(q) for q in questions],
                    "message": "Practice questions selected for your topic."})

init_db()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
