from flask import Flask, request, jsonify, render_template_string, redirect, url_for
import database 

app = Flask(__name__)

# HTML page for task UI
html_page = """
<!DOCTYPE html>
<html>
<head>
  <title>To-Do App</title>
  <link href="https://fonts.googleapis.com/css2?family=Quicksand&display=swap" rel="stylesheet">
  <style>
    body {
      font-family: 'Quicksand', sans-serif;
      background: #fcefee;
      max-width: 600px;
      margin: 40px auto;
      padding: 20px;
      border-radius: 20px;
      box-shadow: 0 0 20px #f4cce2;
    }
    h2, h3 {
      color: #d63384;
      text-align: center;
    }
    input, button {
      padding: 10px;
      margin: 6px 0;
      width: 100%;
      border: 1px solid #ffd6e0;
      border-radius: 10px;
      font-size: 16px;
    }
    button {
      background-color: #ffb6c1;
      color: white;
      border: none;
      cursor: pointer;
      transition: background 0.3s;
    }
    button:hover {
      background-color: #ff8fa3;
    }
    ul {
      list-style: none;
      padding: 0;
    }
    li {
      background: white;
      margin: 10px 0;
      padding: 10px 15px;
      border-left: 6px solid #ffb6c1;
      border-radius: 10px;
      box-shadow: 0 1px 5px rgba(0,0,0,0.1);
    }
  </style>
</head>
<body>
  <h2>To-Do List</h2>
  <form onsubmit="addTask(); return false;">
    <input id="name" placeholder="Who's adding the task?" required />
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
        li.textContent = `${t.name} has added "${t.task}" on ${t.date}`;
        list.appendChild(li);
      });
    }

    async function addTask() {
      const name = document.getElementById("name").value;
      const task = document.getElementById("task").value;
      const date = document.getElementById("date").value;
      await fetch("/tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, task, date })
      });
      document.getElementById("name").value = "";
      document.getElementById("task").value = "";
      document.getElementById("date").value = "";
      loadTasks();
    }

    loadTasks();
  </script>
</body>
</html>
"""

# show task form and list (when opening the page)
@app.route("/")
def ui():
    return render_template_string(html_page)

@app.route("/tasks", methods=["GET"])
def get_tasks():
    tasks = database.get_tasks() # fetch tasks from database
    return jsonify(tasks)

@app.route("/tasks", methods=["POST"])
def post_task():
    data = request.json # read new task from request
    database.add_task(data["name"], data["task"], data["date"]) # save to database
    return jsonify({"message": "Task added succesfully!"}), 201

if __name__ == "__main__":
    database.init_db()
    app.run(debug=True)