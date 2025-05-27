from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret'

applications = {
    'APP123': {'status': 'Approved', 'pet': 'Buddy', 'finalized': False, 'review': None},
    'APP124': {'status': 'Pending', 'pet': 'Milo', 'finalized': False, 'review': None},
    'APP125': {'status': 'Rejected', 'pet': 'Luna', 'finalized': False, 'review': None}
}

meetings = {}

users = {
    'admin': {'password': 'admin123', 'role': 'admin'}
}

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form.get('password')

        if username == 'admin' and password == users['admin']['password']:
            session['role'] = 'admin'
            return redirect(url_for('track_admin'))

        elif username.upper() in applications:
            session['role'] = 'user'
            session['application_id'] = username.upper()
            return redirect(url_for('track_user'))
        else:
            error = "Invalid credentials"

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

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

@app.route('/track_user')
def track_user():
    if 'role' not in session or session['role'] != 'user':
        return redirect(url_for('login'))

    app_id = session['application_id']
    app = applications.get(app_id)
    meetup = meetings.get(app_id)

    return render_template('track_user.html', app_id=app_id, app=app, meetup=meetup)

@app.route('/track_admin')
def track_admin():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    all_data = []
    for app_id, data in applications.items():
        all_data.append({
            'app_id': app_id,
            'pet': data['pet'],
            'status': data['status'],
            'finalized': data['finalized'],
            'review': data['review'],
            'meetup': meetings.get(app_id)
        })

    return render_template('track_admin.html', applications=all_data)

@app.route('/delete/<app_id>', methods=['POST'])
def delete(app_id):
    if 'role' in session and session['role'] == 'admin':
        applications.pop(app_id, None)
        meetings.pop(app_id, None)
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)