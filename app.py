from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3, os, json, random

app = Flask(__name__)
app.secret_key = "quiz_secret_key"

# ---------- DATABASE ----------
def get_db():
    return sqlite3.connect("database.db")

def init_db():
    if not os.path.exists("database.db"):
        db = get_db()
        cur = db.cursor()

        cur.execute("""
            CREATE TABLE students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT
            )
        """)

        cur.execute("""
            CREATE TABLE results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT,
                subject TEXT,
                score INTEGER,
                total INTEGER
            )
        """)

        db.commit()
        db.close()

init_db()

# ---------- LOAD QUESTIONS ----------
def load_questions(subject):
    with open(f"questions/{subject}.json", "r", encoding="utf-8") as f:
        return json.load(f)

# ---------- ROUTES ----------
@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]

        db = get_db()
        cur = db.cursor()
        cur.execute("INSERT INTO students (name, email) VALUES (?,?)", (name, email))
        db.commit()
        db.close()

        session.clear()
        session["student"] = name
        session["used_questions"] = {}

        return redirect("/options")

    return render_template("register.html")

@app.route("/options")
def options():
    if "student" not in session:
        return redirect("/")
    return render_template("options.html")

@app.route("/quiz/<subject>", methods=["GET", "POST"])
def quiz(subject):
    if "student" not in session:
        return redirect("/")

    all_questions = load_questions(subject)

    used = session.get("used_questions", {}).get(subject, [])
    if len(used) >= len(all_questions):
        used = []

    available = [q for i, q in enumerate(all_questions) if i not in used]
    selected = random.sample(available, min(25, len(available)))

    session["current_questions"] = selected
    session["used_questions"][subject] = used + [all_questions.index(q) for q in selected]
    session.modified = True

    if request.method == "POST":
        score = 0
        for i, q in enumerate(session["current_questions"]):
            if request.form.get(f"q{i}") == q["answer"]:
                score += 1

        db = get_db()
        cur = db.cursor()
        cur.execute("""
            INSERT INTO results (student_name, subject, score, total)
            VALUES (?,?,?,?)
        """, (session["student"], subject, score, len(session["current_questions"])))
        db.commit()
        db.close()

        return render_template(
            "result.html",
            subject=subject.capitalize(),
            score=score,
            total=len(session["current_questions"])
        )

    return render_template(
        "quiz.html",
        subject=subject.capitalize(),
        questions=selected,
        duration=600
    )

# ---------- STAFF ----------
@app.route("/staff", methods=["GET", "POST"])
def staff_login():
    if request.method == "POST":
        if request.form["username"] == "staff" and request.form["password"] == "jmc":
            session["staff"] = True
            return redirect("/staff/dashboard")
    return render_template("staff_login.html")

@app.route("/staff/dashboard")
def staff_dashboard():
    if not session.get("staff"):
        return redirect("/staff")

    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT * FROM students")
    students = cur.fetchall()

    cur.execute("SELECT * FROM results")
    results = cur.fetchall()

    cur.execute("SELECT COUNT(DISTINCT student_name) FROM results")
    total_attended = cur.fetchone()[0]

    db.close()

    return render_template(
        "staff_dashboard.html",
        students=students,
        results=results,
        total_attended=total_attended
    )

@app.route("/delete/student/<int:id>")
def delete_student(id):
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM students WHERE id=?", (id,))
    db.commit()
    db.close()
    return redirect("/staff/dashboard")

@app.route("/delete/result/<int:id>")
def delete_result(id):
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM results WHERE id=?", (id,))
    db.commit()
    db.close()
    return redirect("/staff/dashboard")

if __name__ == "__main__":
    app.run(debug=True)
