from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

applications = {
    'APP123': {'status': 'Approved', 'pet': 'Buddy', 'finalized': False},
    'APP124': {'status': 'Pending', 'pet': 'Milo', 'finalized': False},
    'APP125': {'status': 'Rejected', 'pet': 'Luna', 'finalized': False}
}

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
            message = f"Adoption successfully finalized for {app_data['pet']}!"
        else:
            message = f"Adoption already finalized for {app_data['pet']}."
    else:
        message = "Cannot finalize adoption. Not found or not approved."

if __name__ == '__main__':
    app.run(debug=True)