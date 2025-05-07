from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from database import init_db, get_tasks, add_task, add_hardcoded_data, get_user
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required to use sessions

init_db()
add_hardcoded_data()

@app.route("/")
def home():
    if "username" in session:
        return redirect(url_for("task_ui"))
    return render_template("login.html")  # new login page

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    user = get_user(username, password)
    if user:
        session["username"] = username
        return redirect(url_for("task_ui"))
    else:
        return "Invalid credentials. Please try again."

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("home"))

@app.route("/tasks_ui")
def task_ui():
    if "username" not in session:
        return redirect(url_for("home"))
    return render_template("task.html", username=session["username"])

@app.route("/tasks", methods=["GET"])
def get_tasks_route():
    return jsonify([
        {"name": row[0], "task": row[1], "date": row[2]}
        for row in get_tasks()
    ])

@app.route("/tasks", methods=["POST"])
def post_task():
    if "username" not in session:
        return jsonify({"error": "Not logged in"}), 403
    data = request.json
    add_task(session["username"], data["task"], data["date"])
    return jsonify(data), 201

if __name__ == "__main__":
    app.run(debug=True)
