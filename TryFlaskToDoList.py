from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

todos = []

# HTML string (put this near the top, after `todos = []`)
html_page = """
<!DOCTYPE html>
<html>
<head>
  <title>To-Do App</title>
  <style>
    body { font-family: sans-serif; max-width: 500px; margin: 40px auto; }
    li.done { text-decoration: line-through; color: gray; }
  </style>
</head>
<body>
  <h2>Simple To-Do List</h2>
  <input id="taskInput" placeholder="What to do?" />
  <button onclick="addTodo()">Add</button>
  <ul id="todoList"></ul>

  <script>
    async function loadTodos() {
      const res = await fetch("/todos");
      const todos = await res.json();
      const list = document.getElementById("todoList");
      list.innerHTML = "";
      todos.forEach(todo => {
        const li = document.createElement("li");
        li.textContent = todo.task;
        li.className = todo.done ? "done" : "";
        li.onclick = () => markDone(todo.id);
        list.appendChild(li);
      });
    }

    async function addTodo() {
      const input = document.getElementById("taskInput");
      const task = input.value;
      if (!task) return;
      await fetch("/todos", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task })
      });
      input.value = "";
      loadTodos();
    }

    async function markDone(id) {
      await fetch("/todos/" + id, { method: "PATCH" });
      loadTodos();
    }

    loadTodos();
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    return "Welcome to the To-Do API! Try /ui for the frontend"

@app.route("/ui")
def ui():
    return render_template_string(html_page)

@app.route("/todos", methods=["GET"])
def get_todos():
    return jsonify(todos)

@app.route("/todos", methods=["POST"])
def add_todo():
    data = request.json
    todo = {"id": len(todos)+1, "task": data.get("task"), "done": False}
    todos.append(todo)
    return jsonify(todo), 201

@app.route("/todos/<int:todo_id>", methods=["PATCH"])
def mark_done(todo_id):
    for todo in todos:
        if todo["id"] == todo_id:
            todo["done"] = True
            return jsonify(todo)
    return jsonify({"error": "Not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)