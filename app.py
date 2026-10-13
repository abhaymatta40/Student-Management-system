from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Database connection
def get_db_connection():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row
    return conn


# Create database table
def create_table():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            course TEXT NOT NULL,
            marks REAL NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# Home page: Display all students
@app.route("/")
def index():
    conn = get_db_connection()
    students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()

    return render_template("index.html", students=students)


# Add a new student
@app.route("/add", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        course = request.form["course"].strip()
        marks = request.form["marks"]

        if not name or not email or not course or not marks:
            return "Please fill in all fields.", 400

        try:
            marks = float(marks)

            if not 0 <= marks <= 100:
                return "Marks must be between 0 and 100.", 400

        except ValueError:
            return "Please enter valid marks.", 400

        conn = get_db_connection()

        conn.execute(
            "INSERT INTO students (name, email, course, marks) VALUES (?, ?, ?, ?)",
            (name, email, course, marks)
        )

        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    return render_template("add_student.html")


# Search students
@app.route("/search")
def search_student():
    query = request.args.get("q", "").strip()

    conn = get_db_connection()

    students = conn.execute(
        "SELECT * FROM students WHERE name LIKE ? OR email LIKE ?",
        (f"%{query}%", f"%{query}%")
    ).fetchall()

    conn.close()

    return render_template("index.html", students=students, query=query)


# Edit student details
@app.route("/edit/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    conn = get_db_connection()

    student = conn.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    ).fetchone()

    if student is None:
        conn.close()
        return "Student not found.", 404

    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        course = request.form["course"].strip()
        marks = request.form["marks"]

        if not name or not email or not course or not marks:
            conn.close()
            return "Please fill in all fields.", 400

        try:
            marks = float(marks)

            if not 0 <= marks <= 100:
                conn.close()
                return "Marks must be between 0 and 100.", 400

        except ValueError:
            conn.close()
            return "Please enter valid marks.", 400

        conn.execute(
            """
            UPDATE students
            SET name = ?, email = ?, course = ?, marks = ?
            WHERE id = ?
            """,
            (name, email, course, marks, student_id)
        )

        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    conn.close()
    return render_template("edit_student.html", student=student)


# Delete student
@app.route("/delete/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    conn = get_db_connection()

    conn.execute(
        "DELETE FROM students WHERE id = ?",
        (student_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("index"))


if __name__ == "__main__":
    create_table()
    app.run(debug=True)