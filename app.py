from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import database

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # needed for session (session = store information about the user across multiple pages)

# route for login page
@app.route("/", methods=['GET', 'POST']) # get = view, post = submit
def login():
    if request.method == 'POST':
        # extract form data
        username = request.form['username']
        password = request.form['password']
        # check if user exists
        user = database.get_user(username, password)

        if user:
            # store username in session (successful login)
            session["username"] = username 
            return redirect(url_for('ui')) # redirect to task page
        else:
            return "Invalid username or password, please try again."

    # show login form on GET request    
    return render_template('login.html')
    
# route for task (Teha's UI page)
@app.route('/tasks')
def ui():
    # ensure user login session is active
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template("task.html")

if __name__ == "__main__":
    database.init_db()
    database.add_hardcoded_data()
    app.run(debug=True)