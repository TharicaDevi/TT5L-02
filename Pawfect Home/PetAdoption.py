from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import re

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

negeri_daerahs = {
    "Johor": ["Batu Pahat", "Johor Bahru", "Kluang", "Mersing", "Muar", "Pontian", "Segamat", "Kulai", "Tangkak"],
    "Kedah": ["Baling", "Bandar Baharu", "Kota Setar", "Kubang Pasu", "Kuala Muda", "Langkawi", "Padang Terap", "Sik", "Yan"],
    "Kelantan": ["Bachok", "Gua Musang", "Jeli", "Kota Bharu", "Machang", "Pasir Mas", "Pasir Puteh", "Tanah Merah", "Tumpat"],
    "Melaka": ["Alor Gajah", "Jasin", "Melaka Tengah"],
    "Negeri Sembilan": ["Jempol", "Kuala Pilah", "Port Dickson", "Rembau", "Seremban", "Tampin"],
    "Pahang": ["Bentong", "Cameron Highlands", "Jerantut", "Kuantan", "Lipis", "Maran", "Pekan", "Raub", "Temerloh"],
    "Perak": ["Bagan Datuk", "Batang Padang", "Manjung", "Kinta", "Kerian", "Larut, Matang dan Selama", "Hilir Perak", "Perak Tengah", "Kampar"],
    "Perlis": ["Kangar", "Arau"],
    "Pulau Pinang": ["Barat Daya", "Seberang Perai Selatan", "Seberang Perai Tengah", "Seberang Perai Utara", "Timur Laut"],
    "Sabah": ["Kota Kinabalu", "Sandakan", "Tawau", "Keningau", "Lahad Datu", "Kunak", "Beaufort", "Labuan"],
    "Sarawak": ["Kuching", "Miri", "Sibu", "Bintulu", "Sri Aman", "Betong", "Limbang"],
    "Selangor": ["Gombak", "Hulu Langat", "Hulu Selangor", "Klang", "Kuala Langat", "Kuala Lumpur", "Kuala Selangor", "Petaling","Putrajaya", "Sabak Bernam", "Sepang"],
    "Terengganu": ["Besut", "Dungun", "Hulu Terengganu", "Kemaman", "Kuala Terengganu", "Marang"],
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

    selected_state = ''
    city_list = []

    if request.method == 'POST':
        selected_state = request.form.get('state', '').strip()
        city_list = negeri_daerahs.get(selected_state, [])

        if 'final_submit' in request.form:
            date_str = request.form.get('date', '')
            time = request.form.get('time', '')
            phone = request.form.get('phone', '').strip()
            city = request.form.get('city', '').strip()
            notes = request.form.get('notes', '')

            malaysia_phone_regex = re.compile(r'^\+60[1-9][0-9]{7,10}$')

            if not selected_state or not city:
                error = "Please select both State and City."
            elif not malaysia_phone_regex.match(phone):
                error = "Invalid Malaysian phone number format. It should start with +60 followed by 8 to 11 digits."
            else:
                try:
                    chosen_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    today = datetime.today().date()
                    meeting_time = datetime.strptime(time, '%H:%M').time()

                    if chosen_date < today:
                        error = "You cannot schedule a meeting for a past date."
                    elif not (datetime.strptime('08:00', '%H:%M').time() <= meeting_time <= datetime.strptime('22:00', '%H:%M').time()):
                        error = "Meetings must be scheduled between 08:00 and 22:00."
                    else:
                        meetings[application_id] = {
                            'date': chosen_date.strftime('%d/%m/%Y'),
                            'time': time,
                            'phone': phone,
                            'state': selected_state,
                            'city': city,
                            'notes': notes,
                            'approved': True,
                            'by': application_id
                        }
                        success = "Your meeting has been approved!"
                        meeting_info = meetings[application_id]
                except ValueError:
                    error = "Invalid date or time format."

    return render_template(
        'schedule.html',
        application_id=application_id,
        error=error,
        success=success,
        meeting_info=meeting_info,
        state_cities=negeri_daerahs,
        selected_state=selected_state,
        city_list=city_list,
    )

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

    pet_filter = request.args.get('pet_name', '').strip().lower()
    status_filter = request.args.get('status', '').strip().lower()

    filtered_apps = {}
    for app_id, data in applications.items():
        pet_name = data['pet'].lower()
        status = data['status'].lower()

        if pet_filter and pet_filter not in pet_name:
            continue

        if status_filter and status_filter not in status:
            continue

        filtered_apps[app_id] = data

    all_data = []
    for app_id, data in filtered_apps.items():
        all_data.append({
            'app_id': app_id,
            'pet': data['pet'],
            'status': data['status'],
            'finalized': data['finalized'],
            'review': data.get('review'),
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