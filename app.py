from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import database, os, smtplib, random
from email.message import EmailMessage
from database import EMAIL_ADDRESS, EMAIL_PASSWORD

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # needed for session (session = store information about the user across multiple pages)

# folder for uploaded profile pictures
UPLOAD_FOLDER = 'static/profile_pics'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# admin credentials
ADMIN_USERNAME = "TEFadmin"
ADMIN_PASSWORD = "admin@123"

# signup route
@app.route("/signup", methods=['GET', 'POST']) # post = submit
def signup():
    error = None
    if request.method == 'POST':
        # extract form data
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        if not (8 <= len(username) <= 20):
            error = "Username must be 8-20 long!"
        elif not (8 <= len(password) <= 20):
            error = "Password must be 8-20 long!"
        elif database.user_exists(username):
            error = "Username already exists!"
        else: 
            database.add_user(username, password, email)
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

        # check if admin
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["username"] = username
            session["role"] = "admin"
            return redirect(url_for('admin_dashboard'))
        
        # user login
        if user:
            # store username in session (successful login)
            session["username"] = username 
            session["role"] = "user"
            return redirect(url_for('welcome', username=username, success=1))
        else:
            return redirect(url_for('welcome', username=username, success=0))
        
    # show login form on GET request    
    return render_template('login.html')

# request reset route
@app.route("/request_reset", methods=["GET", "POST"])
def request_reset():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]

        if database.validate_username_email(username, email):
            otp = str(random.randint(100000, 999999))
            session["otp"] = otp
            session["reset_email"] = email

            # send OTP to email
            msg = EmailMessage()
            msg.set_content(f"Your OTP is: {otp}")
            msg["Subject"] = "Password Reset OTP"
            msg["From"] = EMAIL_ADDRESS
            msg["To"] = email

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                smtp.send_message(msg)

            return redirect(url_for("verify_otp"))
        else:
            return render_template("reset_request.html", error="Invalid username or email.")

    return render_template("reset_request.html")

# verify OTP route
@app.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():
    if request.method == "POST":
        otp_input = request.form["otp_input"]
        if otp_input == session.get("otp"):
            return redirect(url_for("reset_password"))
        else:
            return render_template("verify_otp.html", error="Incorrect OTP.")
    return render_template("verify_otp.html")

# reset password route
@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    message = ""
    if request.method == "POST":
        new_password = request.form["new_password"]
        email = session.get("reset_email")
        if 8 <= len(new_password) <= 20:
            database.update_password_by_email(email, new_password)
            message = "Password updated successfully. Redirecting to login..."
            return redirect(url_for("login"))
        else:
            message = "Password must be 8-20 characters."
    return render_template("reset.html", error="", message=message)

# welcome route after login
@app.route("/welcome", methods=["GET", "POST"])
def welcome():
    username = request.args.get("username")
    success = request.args.get("success") == "1" # check if login successful
    # welcome page with success/failure message
    return render_template('welcome.html', username=username, success=success)

# admin dashboard route    
@app.route("/admin")
def admin_dashboard():
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    return render_template("admin_dashboard.html")

# add pet route
@app.route("/admin/add_pet", methods=["GET", "POST"])
def add_pet():
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    
    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        breed = request.form["breed"]
        species = request.form["species"]
        gender = request.form["gender"]
        description = request.form["description"]
        image_file = request.files["image"]

        image_filename = ""
        if image_file:
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)
            image_file.save(image_path)

        database.insert_pet(name, age, breed, species, gender, description, image_filename)
        return redirect(url_for("admin_dashboard"))  # Or wherever you show the pet list

    return render_template("add_pet.html")

# update pet details route
@app.route("/admin/update_pet")
def update_pet():
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    return "Update pet info (admin only) - coming soon!"

# review adoption requests route
@app.route("/admin/review_adoptions")
def review_adoptions():
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    return "Review adoption requests (admin only) - coming soon!"

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
    username = session.get("username")
    if not username:
        return redirect(url_for("login"))  # Or your landing page

    if request.method == "POST":
        if "delete" in request.form:
            # account deletion
            database.delete_account(username)
            session.pop("username", None)
            return redirect(url_for("login"))
        # update privacy settings
        visibility = request.form.get("visibility")
        activity_status = request.form.get("activity-status")

        if visibility and activity_status:
            database.update_privacy_settings(username, visibility, activity_status)
            message = "Privacy settings updated!"
            privacy_settings = database.get_privacy_settings(username)
            return render_template("privacy.html", privacy=privacy_settings, message=message)

    # GET request
    privacy_settings = database.get_privacy_settings(username)
    return render_template("privacy.html", privacy=privacy_settings)

# security settings route
@app.route("/security", methods=["GET", "POST"])
def security():
    username = session.get("username")
    if request.method == "POST":
        question = request.form.get("security-question")
        answer = request.form.get("security-answer")

        if username and question and answer:
            database.update_security_settings(username, question, answer)
            user = database.get_user_by_username(username)  # get fresh user data after update
            return render_template("security.html", message="Security settings updated!", user=user)
    
    user = database.get_user_by_username(username) if username else None
    return render_template("security.html", user=user)

# delete account route
@app.route("/delete_account", methods=["POST"])
def delete_account():
    username = session.get('username')
    database.delete_account(username)
    session.pop('username', None)
    flash("Your account has been deleted.")
    return redirect(url_for('login'))

if __name__ == "__main__":
    database.init_db()
    app.run(debug=True)