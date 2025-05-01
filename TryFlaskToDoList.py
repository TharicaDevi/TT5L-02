from flask import Flask, request, jsonify, render_template
import database 

app = Flask(__name__)

# route to show task UI page
@app.route("/tasks_page")
def tasks_page():
    return render_template("task.html")

# route to fetch tasks from database as JSON
@app.route("/tasks", methods=["GET"])
def get_tasks():
    tasks = database.get_tasks() # retrieve all tasks from database
    return jsonify(tasks)

# route to add new task to database
@app.route("/tasks", methods=["POST"])
def post_task():
    data = request.json # read new task from request
    database.add_task(data["name"], data["task"], data["date"]) # save to database
    return jsonify({"message": "Task added succesfully!"}), 201

if __name__ == "__main__":
    database.init_db()
    app.run(debug=True)