from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'

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
        username = request.form['username'].upper()
        password = request.form.get('password')

        if username == 'ADMIN' and password == users['admin']['password']:
            session['role'] = 'admin'
            session['username'] = 'admin'
            return redirect(url_for('track_admin'))

        elif username in applications:
            session['role'] = 'user'
            session['application_id'] = username
            return redirect(url_for('track_user'))

        else:
            error = 'Invalid credentials or Application ID.'

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/track_admin')
def track_admin():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    return render_template('track_admin.html', applications=applications, meetings=meetings)

@app.route('/track_user')
def track_user():
    if session.get('role') != 'user':
        return redirect(url_for('login'))

    app_id = session.get('application_id')
    app_data = applications.get(app_id)
    meetup = meetings.get(app_id)

    return render_template('track_user.html', app_id=app_id, data=app_data, meetup=meetup)