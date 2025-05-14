from flask import Flask, request, jsonify, render_template, redirect, url_for, session
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

    if "username" not in session:
        return redirect(url_for("login"))

    username = session.get("username")
    if request.method == 'POST':
        # extract submitted form data
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        database.update_account_info(username, email, phone, password)
        message = "Changes saved!"

         # retrieve updated user info
        user = database.get_user_by_username(username)
        return render_template('account.html', user=user, message=message)

    user = database.get_user_by_username(username)
    return render_template('account.html', user=user)

# personal info route
@app.route("/personal", methods=["GET", "POST"])
def personal():
    if "username" not in session:
        return redirect(url_for('login'))

    username = session["username"]

    if request.method == "POST":
        username = session["username"]
        fullname = request.form.get("fullname")
        dob = request.form.get("dob")
        gender = request.form.get("gender")
        nationality = request.form.get("nationality")
        language = request.form.get("language")
        bio = request.form.get("bio")

        profile_pic_file = request.files.get("profile-pic")
        profile_pic_path = None

        if profile_pic_file and profile_pic_file.filename != "":
            profile_pic_path = os.path.join(app.config['UPLOAD_FOLDER'], profile_pic_file.filename)
            profile_pic_file.save(profile_pic_path)

        database.update_personal_info(username, fullname, dob, gender, nationality, language, bio, profile_pic_path)

        return redirect(url_for("welcome", username=username, success=1))
    return render_template("personal.html")

# contact info route
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == 'POST':
        username = session.get('username')
        primary = request.form['primary-address']
        shipping = request.form['shipping-address']
        database.update_contact_info(username, primary, shipping)
        return redirect(url_for('contact'))
    return render_template("contact.html")

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