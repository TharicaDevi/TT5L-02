from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from werkzeug.utils import secure_filename
import database, os

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # needed for session (session = store information about the user across multiple pages)

# folder for uploaded profile pictures
UPLOAD_FOLDER = 'static/profile_pics'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
@app.route("/welcome", methods=["GET", "POST"])
def welcome():
    username = request.args.get("username")
    success = request.args.get("success") == "1" # check if login successful
    # welcome page with success/failure message
    return render_template('welcome.html', username=username, success=success)
    
# account info route
@app.route("/account", methods=['GET', 'POST'])
def account():

    username = session.get('username')
    user = database.get_user_by_username(username)  # always define user early
    message = ""

    if request.method == 'POST':
        # extract submitted form data
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        if user:
            database.update_account_info(username, email, phone, password)
            message = "Changes saved!"
            user = database.get_user_by_username(username)
        else:
            message = "User not found. Changes not saved."
    return render_template('account.html', user=user, message=message)

# personal info route
@app.route("/personal", methods=["GET", "POST"])
def personal():
    username = session.get("username")
    user = database.get_user_by_username(username)
    message = ""

    if request.method == "POST":
        fullname = request.form["fullname"]
        dob = request.form["dob"]
        gender = request.form["gender"]
        nationality = request.form["nationality"]
        language = request.form["language"]
        bio = request.form["bio"]

        # handle profile picture
        profile_pic_file = request.files.get("profile-pic")
        profile_pic_path = user[11] if user and len(user) > 11 else None  # default to existing path

        if profile_pic_file and profile_pic_file.filename != "":
            filename = secure_filename(profile_pic_file.filename)
            profile_pic_path = os.path.join("uploads", filename)
            profile_pic_file.save(os.path.join("static", profile_pic_path))

        # update database
        database.update_personal_info(username, fullname, dob, gender, nationality, language, bio, profile_pic_path)

        # fetch updated user info
        user = database.get_user_by_username(username)
        message = "Changes saved!"

    return render_template("personal.html", user=user, message=message)

# contact info route
@app.route("/contact", methods=["GET", "POST"])
def contact():
    username = session.get('username')
    message = ""

    if request.method == 'POST':
        primary = request.form['primary-address']
        shipping = request.form['shipping-address']
        database.update_contact_info(username, primary, shipping)
        message = "Changes saved!"
        # Don't redirect — just reload with the message
        user = database.get_user_by_username(username)
        return render_template("contact.html", user=user, message=message)

    user = database.get_user_by_username(username)
    return render_template("contact.html", user=user)

# privacy settings route
@app.route("/privacy", methods=["GET", "POST"])
def privacy():
    if request.method == 'POST':
        username = session.get('username')
        visibility = request.form.get('visibility')
        activity_status = request.form.get('activity-status')
        database.update_privacy_settings(username, visibility, activity_status)
        return redirect(url_for('privacy')) 
    return render_template("privacy.html")

# security settings route
@app.route("/security", methods=["GET", "POST"])
def security():
    if request.method == "POST":
        username = session.get("username")
        question = request.form.get("security-question")
        answer = request.form.get("security-answer")

        if username and question and answer:
            database.update_security_settings(username, question, answer)
            return render_template("security.html", message="Security settings updated!")
    return render_template("security.html")

if __name__ == "__main__":
    database.init_db()
    app.run(debug=True)