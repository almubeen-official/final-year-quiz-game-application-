from flask import Flask, render_template, request, redirect, session
import sqlite3, os, json

app = Flask(__name__)
app.secret_key = "quiz_secret_key"

# ---------------- DATABASE ---------------- #

def get_db():
    return sqlite3.connect("database.db")


def init_db():

    if not os.path.exists("database.db"):

        db = get_db()
        cur = db.cursor()

        # STUDENTS TABLE
        cur.execute("""
            CREATE TABLE students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                rollno TEXT,
                class TEXT,
                department TEXT
            )
        """)

        # RESULTS TABLE
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

        # 🔥 SAVE SESSION
        session["student"] = student["name"]
        session["student_data"] = student

        # ---------- SAVE JSON ----------
        if not os.path.exists("data/students.json"):
            with open("data/students.json", "w") as f:
                json.dump([], f)

        with open("data/students.json", "r") as f:
            students = json.load(f)

        students.append(student)

        with open("data/students.json", "w") as f:
            json.dump(students, f, indent=4)

        # ---------- SAVE DB ----------
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


# ---------------- QUIZ ---------------- #

@app.route("/quiz/<subject>", methods=["GET", "POST"])
def quiz(subject):

    if "student" not in session:
        return redirect("/")

    # LOAD QUESTIONS
    with open(f"questions/{subject}.json", "r", encoding="utf-8") as f:
        questions = json.load(f)

    # SELECT 25 QUESTIONS
    if "current_questions" not in session:
        selected = questions[:25]
        session["current_questions"] = selected
    else:
        selected = session["current_questions"]

    # ---------- SUBMIT ----------
    if request.method == "POST":

        score = 0

        for i, q in enumerate(selected):
            if request.form.get(f"q{i}") == q["answer"]:
                score += 1

        # GET STUDENT DATA
        student = session.get("student_data")

        if not student:
            student = {
                "name": session.get("student", "Unknown"),
                "rollno": "N/A",
                "class": "N/A",
                "department": "N/A"
            }

        # ---------- SAVE RESULT JSON ----------
        result = {
            "name": student["name"],
            "rollno": student["rollno"],
            "class": student["class"],
            "department": student["department"],
            "subject": subject,
            "score": score,
            "total": len(selected)
        }

        if not os.path.exists("data/results.json"):
            with open("data/results.json", "w") as f:
                json.dump([], f)

        with open("data/results.json", "r") as f:
            results = json.load(f)

        results.append(result)

        with open("data/results.json", "w") as f:
            json.dump(results, f, indent=4)

        # ---------- SAVE RESULT DB ----------
        db = get_db()
        cur = db.cursor()

        cur.execute("""
            INSERT INTO results
            (student_name, rollno, class, department, subject, score, total)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            student["name"],
            student["rollno"],
            student["class"],
            student["department"],
            subject,
            score,
            len(selected)
        ))

        db.commit()
        db.close()

        session.pop("current_questions", None)

        return render_template(
            "result.html",
            score=score,
            total=len(selected),
            student=student
        )

    # SHOW QUIZ
    return render_template(
        "quiz.html",
        questions=selected,
        subject=subject
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
