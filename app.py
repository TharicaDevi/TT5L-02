from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from email.message import EmailMessage
from database import EMAIL_ADDRESS, EMAIL_PASSWORD
from datetime import datetime
import database, os, smtplib, random, re


app = Flask(__name__)
app.secret_key = 'supersecretkey'  # needed for session (session = store information about the user across multiple pages)

# folder for uploaded profile pictures
UPLOAD_FOLDER = 'static/profile_pics'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# admin credentials
ADMIN_USERNAME = "TEFadmin"
ADMIN_PASSWORD = "admin@123"

# -> TEHA'S
applications = {
    'APP123': {'status': 'Approved', 'pet': 'Buddy', 'finalized': False, 'review': None,
               'name': 'Alice', 'email': 'alice@example.com', 'date': '', 'time': '', 'state': '', 'city': '', 'phone': '', 'notes': ''},
    'APP124': {'status': 'Pending', 'pet': 'Milo', 'finalized': False, 'review': None,
               'name': 'Bob', 'email': 'bob@example.com', 'date': '', 'time': '', 'state': '', 'city': '', 'phone': '', 'notes': ''},
    'APP125': {'status': 'Rejected', 'pet': 'Luna', 'finalized': False, 'review': None,
               'name': 'Carol', 'email': 'carol@example.com', 'date': '', 'time': '', 'state': '', 'city': '', 'phone': '', 'notes': ''}
}

meetings = {}

users = {
    'admin': {'password': 'admin123', 'role': 'admin'}
}

state_cities = {
    "Johor": ["Batu Pahat", "Johor Bahru", "Kluang", "Mersing", "Muar", "Pontian", "Segamat", "Kulai", "Tangkak"],
    "Kedah": ["Baling", "Bandar Baharu", "Kota Setar", "Kubang Pasu", "Kuala Muda", "Langkawi", "Padang Terap", "Pendang", "Pokok Sena", "Sik", "Yan"],
    "Kelantan": ["Bachok", "Gua Musang", "Jeli", "Kota Bharu", "Machang", "Pasir Mas", "Pasir Puteh", "Tanah Merah", "Tumpat"],
    "Melaka": ["Alor Gajah", "Jasin", "Melaka Tengah"],
    "Negeri Sembilan": ["Jempol", "Kuala Pilah", "Port Dickson", "Rembau", "Seremban", "Tampin"],
    "Pahang": ["Bentong", "Cameron Highlands", "Jerantut", "Kuantan", "Lipis", "Maran", "Pekan", "Raub", "Rompin", "Temerloh", "Bera"],
    "Perak": ["Bagan Datuk", "Batang Padang", "Hilir Perak", "Kampar", "Kerian", "Kinta", "Kuala Kangsar", "Larut, Matang dan Selama", "Manjung", "Muallim", "Perak Tengah"],
    "Perlis": ["Kangar", "Arau", "Padang Besar"],
    "Pulau Pinang": ["Timur Laut", "Barat Daya", "Seberang Perai Utara", "Seberang Perai Tengah", "Seberang Perai Selatan"],
    "Sabah": ["Beaufort", "Beluran", "Keningau", "Kota Belud", "Kota Kinabalu", "Kota Marudu", "Kuala Penyu", "Kudat", "Kunak", "Lahad Datu", "Nabawan", "Papar", "Penampang", "Pitas", "Putatan", "Ranau", "Sandakan", "Semporna", "Sipitang", "Tambunan", "Tawau", "Tenom", "Tongod", "Tuaran"],
    "Sarawak": ["Betong", "Bintulu", "Kapit", "Kuching", "Limbang", "Miri", "Mukah", "Samarahan", "Sarikei", "Serian", "Sibu", "Sri Aman"],
    "Selangor": ["Gombak", "Hulu Langat", "Hulu Selangor", "Klang", "Kuala Langat", "Kuala Selangor", "Petaling", "Sabak Bernam", "Sepang"],
    "Terengganu": ["Besut", "Dungun", "Hulu Terengganu", "Kemaman", "Kuala Terengganu", "Marang", "Setiu"],
    "Kuala Lumpur": ["Bukit Bintang", "Cheras", "Kepong", "Lembah Pantai", "Sentul", "Setapak", "Titiwangsa", "Wangsa Maju"],
    "Putrajaya": ["Putrajaya"],
    "Labuan": ["Labuan"]
}

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

        # check if admin
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["username"] = username
            session["role"] = "admin"
            return redirect(url_for('admin_dashboard'))

        # check if user exists
        user = database.get_user(username, password)

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
        age = int(request.form["age"])
        breed = request.form["breed"]
        pet_type = request.form["type"]
        color = request.form["color"]
        status = request.form["status"]
        image_file = request.files["picture"]

        image_filename = ""
        if image_file:
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)
            image_file.save(image_path)

        database.insert_pet(name, image_filename, pet_type, color, breed, age, status)
        
        flash("The pet has been successfully added!")
        return redirect(url_for("view_pets"))

    return render_template("add_pet.html")

# view pets route
@app.route("/view_pets")
def view_pets():
    pets = database.get_all_pets()
    return render_template("view_pets.html", pets=pets)

# update pet details route
@app.route("/admin/update_pet")
def update_pet():
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    return "Update pet info (admin only) - coming soon!"

# review adoption requests route -> TEHA'S
@app.route("/admin/review_adoptions")
def track_admin():
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    search_name = request.args.get('search_name', '').strip().lower()
    search_email = request.args.get('search_email', '').strip().lower()
    filter_state = request.args.get('filter_state', '').strip()

    filtered_apps = {}
    for app_id, data in applications.items():
        if search_name and search_name not in data.get('name', '').lower():
            continue
        if search_email and search_email not in data.get('email', '').lower():
            continue
        if filter_state and filter_state != data.get('state', ''):
            continue
        filtered_apps[app_id] = data

    all_data = [
        {
            'app_id': app_id,
            'name': data.get('name', ''),
            'email': data.get('email', ''),
            'date': data.get('date', ''),
            'time': data.get('time', ''),
            'state': data.get('state', ''),
            'city': data.get('city', ''),
            'phone': data.get('phone', ''),
            'notes': data.get('notes', ''),
            'pet': data['pet'],
            'status': data['status'],
            'finalized': data['finalized'],
            'review': data.get('review'),
            'meetup': meetings.get(app_id)
        }
        for app_id, data in filtered_apps.items()
    ]

    return render_template('track_admin.html', applications=all_data, state_cities=state_cities)

# edit meeting route -> TEHA'S
@app.route('/edit_meeting/<app_id>', methods=['GET', 'POST'])
def edit_meeting(app_id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    meeting = meetings.get(app_id)
    if not meeting:
        return "No meeting found to edit.", 404

    error = None
    success = None
    selected_state = meeting.get('state', '')
    city_list = state_cities.get(selected_state, [])

    if request.method == 'POST':
        date_str = request.form.get('date', '')
        time_str = request.form.get('time', '')
        phone = request.form.get('phone', '').strip()
        state = request.form.get('state', '')
        city = request.form.get('city', '')
        notes = request.form.get('notes', '')

        malaysia_phone_regex = re.compile(r'^\+60[1-9][0-9]{7,10}$')

        if not state or not city:
            error = "Please select both State and City."
        elif not malaysia_phone_regex.match(phone):
            error = "Invalid phone number format. It must be +60 followed by 8-11 digits."
        else:
            try:
                meeting_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                today = datetime.today().date()
                meeting_time = datetime.strptime(time_str, '%H:%M').time()

                if meeting_date < today:
                    error = "Cannot choose a past date."
                elif not (datetime.strptime('08:00', '%H:%M').time() <= meeting_time <= datetime.strptime('22:00', '%H:%M').time()):
                    error = "Meeting time must be between 08:00 and 22:00."
                else:
                    meetings[app_id].update({
                        'date': date_str,
                        'time': time_str,
                        'phone': phone,
                        'state': state,
                        'city': city,
                        'notes': notes,
                    })
                    success = "Meeting updated successfully!"
                    selected_state = state
                    city_list = state_cities.get(state, [])

            except ValueError:
                error = "Invalid date or time format."

    return render_template('edit_meeting.html',
        app_id=app_id,
        meeting=meetings.get(app_id),
        error=error,
        success=success,
        state_cities=state_cities,
        selected_state=selected_state,
        city_list=city_list,
    )

# delete meeting route -> TEHA'S
@app.route('/delete-meeting/<app_id>', methods=['GET'])
def delete_meeting(app_id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    if app_id in meetings:
        del meetings[app_id]

    if app_id in applications:
        del applications[app_id]

    return redirect(url_for('track_admin'))

# user dashboard route
@app.route("/user", methods=['GET', 'POST'])
def user_dashboard():
    if session.get("role") != "user":
        return redirect(url_for("login"))
    return render_template("user_dashboard.html")

# adoption application route -> TEHA'S
@app.route('/track_user')
def track_user():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))

    user = database.get_user_by_username(username)
    if not user:
        return redirect(url_for('login'))

    app_id = session.get('application_id')
    app = applications.get(app_id)
    meetup = meetings.get(app_id)

    return render_template('track_user.html', username=user[1], app_id=app_id, app=app, meetup=meetup)

# schedule meeting route -> TEHA'S
@app.route('/schedule/<application_id>', methods=['GET', 'POST'])
def schedule(application_id):
    if session.get('role') != 'user' or session.get('application_id') != application_id:
        return redirect(url_for('login'))

    error = None
    success = None
    selected_state = ''
    city_list = []
    meeting = meetings.get(application_id, {})

    if request.method == 'POST':
        selected_state = request.form.get('state', '').strip()
        city_list = state_cities.get(selected_state, [])

        final_submit = request.form.get('final_submit', '')

        date_str = request.form.get('date', '')
        time_str = request.form.get('time', '')
        phone = request.form.get('phone', '').strip()
        city = request.form.get('city', '').strip()
        notes = request.form.get('notes', '')

        meeting = {
            'date': date_str,
            'time': time_str,
            'phone': phone,
            'state': selected_state,
            'city': city,
            'notes': notes,
            'approved': meetings.get(application_id, {}).get('approved', False),
            'by': application_id
        }

        if final_submit == 'update_state':
            return render_template('schedule.html',
                application_id=application_id,
                error=None,
                success=None,
                meeting=meeting,
                state_cities=state_cities,
                selected_state=selected_state,
                city_list=city_list
            )

        malaysia_phone_regex = re.compile(r'^\+60[1-9][0-9]{7,10}$')

        if not selected_state or not city:
            error = "Please select both State and City."
        elif not malaysia_phone_regex.match(phone):
            error = "Invalid Malaysian phone number format. Format: +60XXXXXXXXX."
        else:
            try:
                chosen_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                today = datetime.today().date()
                meeting_time = datetime.strptime(time_str, '%H:%M').time()

                if chosen_date < today:
                    error = "Cannot schedule a meeting for a past date."
                elif not (datetime.strptime('08:00', '%H:%M').time() <= meeting_time <= datetime.strptime('22:00', '%H:%M').time()):
                    error = "Meetings must be scheduled between 08:00 and 22:00."
                else:
                    meeting['approved'] = (final_submit == 'finalize')
                    meetings[application_id] = meeting
                    success = "Your meeting has been finalized!" if final_submit == 'finalize' else "Your meeting has been saved!"
            except ValueError:
                error = "Invalid date or time format."

    else:
        if meeting:
            selected_state = meeting.get('state', '')
            city_list = state_cities.get(selected_state, [])
        else:
            meeting = None

    return render_template('schedule.html',
        application_id=application_id,
        error=error,
        success=success,
        meeting=meeting,
        state_cities=state_cities,
        selected_state=selected_state,
        city_list=city_list
    )

#
@app.route('/finalize', methods=['POST'])
def finalize():
    app_id = request.form.get('application_id', '').strip().upper()
    app_data = applications.get(app_id)
    if not app_data:
        return "Application ID not found.", 404
    if app_data["status"] != "Approved":
        return "Application not approved. Cannot finalize.", 403
    if app_data['finalized']:
        return f"Adoption already finalized for {app_data['pet']}."
    app_data['finalized'] = True
    session['application_id'] = app_id
    return redirect(url_for('schedule', application_id=app_id))


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

        if user:
            database.update_account_info(username, email, phone) 
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

# delete account route
@app.route("/delete_account", methods=["POST"])
def delete_account():
    username = session.get('username')
    database.delete_account(username)
    session.pop('username', None)
    flash("Your account has been deleted.")
    return redirect(url_for('login'))

if __name__ == "__main__":
    database.init_info_db()
    database.init_pets_db()
    database.init_adoptions_db()
    app.run(debug=True)