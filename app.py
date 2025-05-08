from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import database

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # needed for session (session = store information about the user across multiple pages)

# home route
@app.route("/", methods=['GET']) # get = view
def home():
    return render_template('home.html')

# signup route
@app.route("/signup", methods=['GET', 'POST']) # post = submit
def signup():
    if request.method == 'POST':
        # extract form data
        username = request.form['username']
        password = request.form['password']
        try:
            # add new user to database
            database.add_user(username, password)
            # successful, redirect to login page
            return redirect(url_for('login'))
        except:
            # unsuccessful, retry signup
            return "Username already exists. Please choose a different one."
    return render_template('signup.html')

# login route
@app.route("/login", methods=['GET', 'POST']) 
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