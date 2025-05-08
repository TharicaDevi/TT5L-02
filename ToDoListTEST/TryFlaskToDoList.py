from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from database import init_db, get_user, add_user, add_task, get_tasks_by_user
import sqlite3

app = Flask(__name__)
app.secret_key = "your-secret-key"  # Required for session to work

init_db()

@app.route("/")
def index():
    if "username" in session:
        return redirect("/tasks")
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = get_user(username, password)
        if user:
            session["username"] = username
            return redirect("/tasks")
        return "Invalid credentials"
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/tasks")
def task_ui():
    if "username" not in session:
        return redirect("/login")
    return render_template("task.html", username=session["username"])

@app.route("/api/tasks", methods=["GET"])
def get_user_tasks():
    if "username" not in session:
        return jsonify([])
    return jsonify(get_tasks_by_user(session["username"]))

@app.route("/api/tasks", methods=["POST"])
def post_task():
    if "username" not in session:
        return "Not logged in", 403
    data = request.json
    add_task(session["username"], data["task"], data["date"])
    return jsonify(data), 201

if __name__ == "__main__":
    app.run(debug=True)
