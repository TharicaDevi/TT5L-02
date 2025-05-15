from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret'

applications = {
    'APP123': {'status': 'Approved', 'pet': 'Buddy', 'finalized': False, 'user_id': 'user001'},
    'APP124': {'status': 'Pending', 'pet': 'Milo', 'finalized': False, 'user_id': 'user002'},
    'APP125': {'status': 'Rejected', 'pet': 'Luna', 'finalized': False, 'user_id': 'user003'}
}


meetings = {}
reviews = {}

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    app_id = ''
    show_finalize = False
    message = None

    if request.method == 'POST':
        app_id = request.form['application_id'].strip().upper()
        app_data = applications.get(app_id)

        if app_data:
            if app_data['finalized']:
                result = f"Adoption already finalized for {app_data['pet']}"
            else:
                result = f"{app_data['status']} for pet {app_data['pet']}"
                if app_data['status'] == 'Approved':
                    show_finalize = True
        else:
            result = "Application ID not found"

    return render_template('index.html', status=result, app_id=app_id, show_finalize=show_finalize, message=message)

@app.route('/finalize', methods=['POST'])
def finalize():
    app_id = request.form['application_id'].strip().upper()
    app_data = applications.get(app_id)

    if app_data and app_data["status"] == "Approved":
        if not app_data['finalized']:
            app_data['finalized'] = True
            session['application_id'] = app_id
            session['user_id'] = app_data['user_id']
            return redirect(url_for('schedule', application_id=app_id))
        else:
            return f"Adoption already finalized for {app_data['pet']}."
    return "Cannot finalize adoption. Not found or not approved."

@app.route('/schedule/<application_id>', methods=['GET', 'POST'])
def schedule(application_id):
    if 'application_id' not in session or session['application_id'] != application_id:
        return redirect(url_for('index'))

    error = None
    success = None
    meeting_info = None

    if request.method == 'POST':
        date_str = request.form['date']
        time = request.form['time']
        notes = request.form.get('notes', '')

        try:
            chosen_date = datetime.strptime(date_str, '%d/%m/%Y').date()
            today = datetime.today().date()

            if chosen_date < today:
                error = "You cannot schedule a meeting for a past date."
            else:
                meetings[application_id] = {
                    'date': date_str,
                    'time': time,
                    'notes': notes,
                    'approved': True,
                    'by_user': session['user_id']
                }
                success = "Your meeting has been approved!"
                meeting_info = meetings[application_id]
        except ValueError:
            error = "Invalid date format. Please use DD/MM/YYYY."

    return render_template('schedule.html', application_id=application_id, error=error, success=success, meeting_info=meeting_info)

@app.route('/track')
def track():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('index'))

    user_apps = {k:v for k,v in applications.items() if v['user_id'] == user_id}
    user_meetings = {k:v for k,v in meetings.items() if applications.get(k, {}).get('user_id') == user_id}

    return render_template('track.html', applications=user_apps, meetings=user_meetings)


if __name__ == '__main__':
    app.run(debug=True)