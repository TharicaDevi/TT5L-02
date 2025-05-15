from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'secret'

applications = {
    'APP123': {'status': 'Approved', 'pet': 'Buddy', 'finalized': False},
    'APP124': {'status': 'Pending', 'pet': 'Milo', 'finalized': False},
    'APP125': {'status': 'Rejected', 'pet': 'Luna', 'finalized': False}
}

meetings = {}

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
            return redirect(url_for('schedule', application_id=app_id))
        else:
            return f"Adoption already finalized for {app_data['pet']}."
    return "Cannot finalize adoption. Not found or not approved."


@app.route('/schedule/<application_id>', methods=['GET', 'POST'])
def schedule(application_id):
    if application_id not in session:
        return redirect(url_for('login'))

    error = None
    if request.method == 'POST':
        date_str = request.form['date']
        time = request.form['time']
        notes = request.form['notes']

        try:
            chosen_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            tomorrow = datetime.today().date() + timedelta(days=1)

            if chosen_date < tomorrow:
                error = "You cannot schedule a meeting for today or a past date."
            else:
                schedule_meeting(session['user_id'], date_str, time, notes)
                return redirect(url_for('track')) 
        except ValueError:
            error = "Invalid date format."

    return render_template('schedule.html', application_id=application_id, error=error)


if __name__ == '__main__':
    app.run(debug=True)
