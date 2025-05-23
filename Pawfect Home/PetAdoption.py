from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

applications = {
    'APP123': {'status': 'Approved', 'pet': 'Buddy', 'finalized': False, 'review': None},
    'APP124': {'status': 'Pending', 'pet': 'Milo', 'finalized': False, 'review': None},
    'APP125': {'status': 'Rejected', 'pet': 'Luna', 'finalized': False, 'review': None}
}

meetings = {}

users = {
    'admin': {'password': 'admin123', 'role': 'admin'},
}

@app.route('/', methods=['GET', 'POST'])
def index():
    status = None
    app_id = None
    show_finalize = False

    if request.method == 'POST':
        app_id = request.form['application_id'].strip().upper()
        app_data = applications.get(app_id)

        if app_data:
            status = app_data['status']
            if app_data['status'] == 'Approved' and not app_data['finalized']:
                show_finalize = True
        else:
            status = "Application ID not found."

    return render_template('index.html', status=status, app_id=app_id, show_finalize=show_finalize)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        session["username"] = username

        if username == "admin":
            return redirect(url_for("track_admin"))
        else:
            return redirect(url_for("track_user"))

    return render_template("login.html")

@app.route('/finalize', methods=['POST'])
def finalize():
    app_id = request.form['application_id'].strip().upper()
    app_data = applications.get(app_id)

    if app_data and app_data["status"] == "Approved":
        if not app_data['finalized']:
            app_data['finalized'] = True
            session['application_id'] = app_id
            return redirect(url_for('schedule', application_id=app_id))
        else:
            return f"Adoption already finalized for {app_data['pet']}."
    return "Cannot finalize adoption. Not found or not approved."

@app.route('/schedule/<application_id>', methods=['GET', 'POST'])
def schedule(application_id):
    if 'application_id' not in session or session['application_id'] != application_id:
        return redirect(url_for('login'))

    error = None
    success = None
    meeting_info = None

    if request.method == 'POST':
        date_str = request.form['date']
        time = request.form['time']
        notes = request.form['notes']

        try:
            chosen_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            today = datetime.today().date()

            meeting_time = datetime.strptime(time, '%H:%M').time()
            if not (datetime.strptime('08:00', '%H:%M').time() <= meeting_time <= datetime.strptime('22:00', '%H:%M').time()):
                error = "Meetings must be scheduled between 08:00 and 22:00."
            elif chosen_date < today:
                error = "You cannot schedule a meeting for a past date."
            else:
                meetings[application_id] = {
                    'date': chosen_date.strftime('%d/%m/%Y'),
                    'time': time,
                    'notes': notes,
                    'approved': True,
                    'by': application_id
                }
                success = "Your meeting has been approved!"
                meeting_info = meetings[application_id]
        except ValueError:
            error = "Invalid date or time format."

    return render_template('schedule.html', application_id=application_id, error=error, success=success, meeting_info=meeting_info)

@app.route("/track_user")
def track_user():
    username = session.get("username")
    if not username or username == "admin":
        return redirect(url_for("login"))
    user_apps = [app for app in applications if app.app_id == username]
    return render_template("track_user.html", applications=user_apps)

@app.route("/track_admin")
def track_admin():
    username = session.get("username")
    if username != "admin":
        return redirect(url_for("login"))
    return render_template("track_admin.html", applications=applications)

@app.route('/delete/<application_id>', methods=['POST'])
def delete(application_id):
    if 'role' in session and session['role'] == 'admin':
        applications.pop(application_id, None)
        meetings.pop(application_id, None)
    return redirect(url_for('track_admin'))

@app.route('/submit_review', methods=['POST'])
def submit_review():
    app_id = request.form['application_id']
    feedback = request.form['feedback']

    if app_id in applications and applications[app_id]['finalized']:
        applications[app_id]['review'] = {
            'by': app_id,
            'feedback': feedback
        }

    if session.get('role') == 'admin':
        return redirect(url_for('track_admin'))
    return redirect(url_for('track_user'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)