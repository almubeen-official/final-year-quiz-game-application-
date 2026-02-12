from flask import Flask, render_template, request, redirect, session
import sqlite3, os, json, random

app = Flask(__name__)
app.secret_key = "quiz_secret_key"

# ---------------- DATABASE ---------------- #

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
                rollno TEXT,
                class TEXT,
                department TEXT
            )
        """)

        cur.execute("""
            CREATE TABLE results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT,
                rollno TEXT,
                class TEXT,
                department TEXT,
                subject TEXT,
                score INTEGER,
                total INTEGER
            )
        """)

        db.commit()
        db.close()


init_db()

# ---------------- DASHBOARD ---------------- #

@app.route("/")
def dashboard():
    return render_template("dashboard.html")


# ---------------- REGISTER ---------------- #

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        student = {
            "rollno": request.form["rollno"],
            "name": request.form["name"],
            "class": request.form["classname"],
            "department": request.form["department"]
        }

        session["student"] = student["name"]
        session["student_data"] = student

        # SAVE DB
        db = get_db()
        cur = db.cursor()

        cur.execute("""
            INSERT INTO students (name, rollno, class, department)
            VALUES (?, ?, ?, ?)
        """, (
            student["name"],
            student["rollno"],
            student["class"],
            student["department"]
        ))

        db.commit()
        db.close()

        return redirect("/options")

    return render_template("register.html")


# ---------------- OPTIONS ---------------- #

@app.route("/options")
def options():

    if "student" not in session:
        return redirect("/")

    return render_template("options.html")
@app.route("/quiz/<subject>", methods=["GET", "POST"])
def quiz(subject):
    if "student" not in session:
        return redirect("/")

    # 1. LOAD ALL QUESTIONS FIRST
    with open(f"questions/{subject}.json", "r", encoding="utf-8") as f:
        questions = json.load(f)

    # 2. GET SELECTED INDEXES FROM SESSION
    if request.method == "GET":
        session.pop("question_indexes", None)
        indexes = random.sample(
            range(len(questions)),
            min(30, len(questions))
        )
        session["question_indexes"] = indexes
    
    # Always get indexes for both GET and POST
    indexes = session.get("question_indexes", [])
    selected = [questions[i] for i in indexes]

    # 3. ---------- SUBMIT LOGIC ----------
    if request.method == "POST":
        score = 0
        student_data = session.get("student_data")

        # Score Calculation
        for i, q in enumerate(selected):
            user_ans = request.form.get(f"q{i}")
            if user_ans == q["answer"]:
                score += 1

        # SAVE TO DATABASE (Idhu dhaan missing-ah irundhuchi)
        db = get_db()
        cur = db.cursor()
        cur.execute("""
            INSERT INTO results (student_name, rollno, class, department, subject, score, total)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            student_data["name"],
            student_data["rollno"],
            student_data["class"],
            student_data["department"],
            subject.capitalize(),
            score,
            len(selected)
        ))
        db.commit()
        db.close()

        # Render result page with all data
        return render_template(
            "result.html",
            score=score,
            total=len(selected),
            student=student_data,
            subject=subject.capitalize()
        )

    # 4. ---------- RENDER QUIZ PAGE (GET) ----------
    return render_template(
        "quiz.html",
        questions=selected,
        subject=subject,
        duration=600
    )


# ---------------- STAFF LOGIN ---------------- #

@app.route("/staff", methods=["GET", "POST"])
def staff_login():

    if request.method == "POST":

        if request.form["username"] == "staff" and request.form["password"] == "jmc":
            session["staff"] = True
            return redirect("/staff/dashboard")

    return render_template("staff_login.html")


# ---------------- STAFF DASHBOARD ---------------- #

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


# ---------------- DELETE ---------------- #

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


# ---------------- RUN ---------------- #

if __name__ == "__main__":
    app.run(debug=True)
