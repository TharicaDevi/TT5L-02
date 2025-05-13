from flask import Flask, render_template, request

app = Flask(__name__)

applications = {
    'APP123': {'status': 'Approved', 'pet': 'Buddy'},
    'APP124': {'status': 'Pending', 'pet': 'Milo'},
    'APP125': {'status': 'Rejected', 'pet': 'Luna'}
}

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        app_id = request.form['application_id'].strip().upper()
        app_data = applications.get(app_id)
        if app_data:
            result = f"{app_data['status']} for pet {app_data['pet']}"
        else:
            result = "Application ID not found"
    return render_template('index.html', status=result)

if __name__ == '__main__':
    app.run(debug=True)
