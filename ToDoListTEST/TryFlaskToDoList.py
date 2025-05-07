from flask import Flask, request, jsonify, render_template
from database import init_db, get_tasks, add_task, add_hardcoded_data

app = Flask(__name__)

init_db()
add_hardcoded_data()

@app.route("/")
def ui():
    return render_template("task.html")

@app.route("/tasks", methods=["GET"])
def get_tasks_route():
    all_tasks = get_tasks()
    task_list = [{"name": row[0], "task": row[1], "date": row[2]} for row in all_tasks]
    return jsonify(task_list)

@app.route("/tasks", methods=["POST"])
def post_task():
    data = request.json
    add_task(data["name"], data["task"], data["date"])
    return jsonify(data), 201

if __name__ == "__main__":
    app.run(debug=True)
