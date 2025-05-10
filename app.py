from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import database

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # needed for session (session = store information about the user across multiple pages)

# signup route
@app.route("/signup", methods=['GET', 'POST']) # post = submit
def signup():
    error = None
    if request.method == 'POST':
        # extract form data
        username = request.form['username']
        password = request.form['password']

        if not (8 <= len(username) <= 20):
            error = "Username must be 8-20 long!"
        elif not (8 <= len(password) <= 20):
            error = "Password must be 8-20 long!"
        elif database.user_exists(username):
            error = "Username already exists!"
        else: 
            database.add_user(username, password)
            return redirect(url_for('login'))
    return render_template('signup.html', error=error)

# login route
@app.route("/", methods=['GET', 'POST']) 
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
            return redirect(url_for('welcome', username=username, success=1))
        else:
            return redirect(url_for('welcome', username=username, success=0))
        
    # show login form on GET request    
    return render_template('login.html')

# reset password route
@app.route("/reset", methods=['GET', 'POST'])
def reset():
    error = None
    message = None

    if request.method == 'POST':
        username = request.form['username']
        new_password = request.form['new_password']

        if not (8 <= len(new_password) <= 20):
            error = "Password must be 8-20 characters!"
        elif not database.user_exists(username):
            error = "Username doesn't exist!"
        else:
            database.update_password(username, new_password)
            message = "Password successfully updated! Redirecting to login page..."

    return render_template('reset.html', error=error, message=message)

# welcome route after login
@app.route("/welcome")
def welcome():
    username = request.args.get("username")
    success = request.args.get("success") == "1" # check if login successful
    # welcome page with success/failure message
    return render_template('welcome.html', username=username, success=success)
    
# route for task (Teha's UI page)
@app.route('/tasks')
def ui():
    # ensure user login session is active
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template("task.html")

if __name__ == "__main__":
    database.init_db()
    app.run(debug=True)
