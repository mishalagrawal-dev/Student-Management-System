
from flask import Flask, render_template, request, redirect
import pymysql
import os
import time

app = Flask(__name__)


def get_db():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "db"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "root"),
        database=os.getenv("DB_NAME", "students"),
        cursorclass=pymysql.cursors.DictCursor
    )


def initialize_db():
    for _ in range(20):
        try:
            db = get_db()
            cursor = db.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100),
                    roll VARCHAR(50),
                    course VARCHAR(100)
                )
            """)

            db.commit()
            cursor.close()
            db.close()
            print("Database initialized successfully!")
            return

        except pymysql.MySQLError as e:
            print("Waiting for database:", e)
            time.sleep(2)

    raise RuntimeError("Could not connect to MySQL")


@app.route("/")
def home():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("index.html", students=students)


@app.route("/add", methods=["POST"])
def add():
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO students (name, roll, course) VALUES (%s, %s, %s)",
        (
            request.form["name"],
            request.form["roll"],
            request.form["course"]
        )
    )

    db.commit()
    cursor.close()
    db.close()

    return redirect("/")


@app.route("/delete/<int:id>")
def delete(id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("DELETE FROM students WHERE id = %s", (id,))

    db.commit()
    cursor.close()
    db.close()

    return redirect("/")


if __name__ == "__main__":
    initialize_db()
    app.run(host="0.0.0.0", port=5000)
