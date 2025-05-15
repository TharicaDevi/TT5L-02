from flask import Flask, render_template, request, redirect, url_for, session

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
    if application_id not in applications or not applications[application_id]['finalized']:
        return "Invalid application or not finalized yet"

    if request.method == 'POST':
        date = request.form['date']
        time = request.form['time']
        notes = request.form['notes']

        meetings[application_id] = {
            'date': date,
            'time': time,
            'notes': notes
        }

        return f"Meeting scheduled for {applications[application_id]['pet']} on {date} at {time}"

    return render_template('schedule.html', application_id=application_id)


if __name__ == '__main__':
    app.run(debug=True)
