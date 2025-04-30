from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

tasks = []

html_page = """
<!DOCTYPE html>
<html>
<head>
  <title>Task Tracker</title>
  <style>
    body { font-family: sans-serif; max-width: 600px; margin: 40px auto; }
    input, button { padding: 8px; margin: 5px; width: 100%; }
    li { margin: 8px 0; }
  </style>
</head>
<body>
  <h2>Add New Task</h2>
  <form onsubmit="addTask(); return false;">
    <input id="name" placeholder="Who is adding the task?" required />
    <input id="task" placeholder="What is the task?" required />
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

@app.route("/")
def ui():
    return render_template_string(html_page)

@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify(tasks)

@app.route("/tasks", methods=["POST"])
def post_task():
    data = request.json
    new_task = {
        "name": data["name"],
        "task": data["task"],
        "date": data["date"]
    }
    tasks.append(new_task)
    return jsonify(new_task), 201

if __name__ == "__main__":
    app.run(debug=True)
