from flask import Flask, request, jsonify, render_template_string, session, redirect
from db_helper import get_tasks as db_get_tasks, add_task as db_add_task

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Needed to use sessions

# --- HTML page template ---
html_page = """
<!DOCTYPE html>
<html>
<head>
  <title>To-Do App</title>
  <link href="https://fonts.googleapis.com/css2?family=Quicksand&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Quicksand', sans-serif; background: #fcefee; max-width: 600px; margin: 40px auto; padding: 20px; border-radius: 20px; box-shadow: 0 0 20px #f4cce2; }
    h2, h3 { color: #d63384; text-align: center; }
    input, button { padding: 10px; margin: 6px 0; width: 100%; border: 1px solid #ffd6e0; border-radius: 10px; font-size: 16px; }
    button { background-color: #ffb6c1; color: white; border: none; cursor: pointer; transition: background 0.3s; }
    button:hover { background-color: #ff8fa3; }
    ul { list-style: none; padding: 0; }
    li { background: white; margin: 10px 0; padding: 10px 15px; border-left: 6px solid #ffb6c1; border-radius: 10px; box-shadow: 0 1px 5px rgba(0,0,0,0.1); }
  </style>
</head>
<body>
  <h2>Hi {{ username }}!</h2>
  <form onsubmit="addTask(); return false;">
    <input id="task" placeholder="Write your task here" required />
    <input id="date" type="date" required />
    <button type="submit">Add Task</button>
  </form>

  <h3>Task List</h3>
  <ul id="taskList"></ul>

  <script>
    async function loadTasks() {
      const res = await fetch("/tasks");
      const tasks = await res.json();
      const list = document.getElementById("taskList");
      list.innerHTML = "";
      tasks.forEach(t => {
        const li = document.createElement("li");
        li.textContent = `${t.username} added "${t.task}" on ${t.date}`;
        list.appendChild(li);
      });
    }

    async function addTask() {
      const task = document.getElementById("task").value;
      const date = document.getElementById("date").value;
      await fetch("/tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task, date })
      });
      document.getElementById("task").value = "";
      document.getElementById("date").value = "";
      loadTasks();
    }

    loadTasks();
  </script>
</body>
</html>
"""

# --- Routes ---

@app.route("/")
def ui():
    username = session.get("username")
    if not username:
        return redirect("/login")  # redirect if not logged in
    return render_template_string(html_page, username=username)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        # In real app: validate password too
        if username:
            session["username"] = username
            return redirect("/")
        return "Invalid login", 401
    return """
    <form method="POST">
        <input name="username" placeholder="Enter username" required>
        <button type="submit">Login</button>
    </form>
    """

@app.route("/tasks", methods=["GET"])
def get_tasks():
    tasks = db_get_tasks()
    return jsonify([
        {"username": t[0], "task": t[1], "date": t[2]} for t in tasks
    ])

@app.route("/tasks", methods=["POST"])
def post_task():
    data = request.json
    username = session.get("username")
    if not username:
        return "Unauthorized", 401
    db_add_task(username, data["task"], data["date"])
    return jsonify({"username": username, "task": data["task"], "date": data["date"]}), 201

if __name__ == "__main__":
    app.run(debug=True)
