from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'

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

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form.get('password', '')

        if username == 'admin' and password == users['admin']['password']:
            session['role'] = 'admin'
            return redirect(url_for('track_admin'))
        elif username.upper() in applications:
            session['role'] = 'user'
            session['application_id'] = username.upper()
            return redirect(url_for('track_user'))
        else:
            error = "Invalid credentials."
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

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

        # Store current form state regardless of full submission or just state update
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
            # Only updating state and city list; skip validation
            return render_template(
                'schedule.html',
                application_id=application_id,
                error=None,
                success=None,
                meeting=meeting,
                state_cities=state_cities,
                selected_state=selected_state,
                city_list=city_list
            )

        # Proceed with full validation
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

    return render_template(
        'schedule.html',
        application_id=application_id,
        error=error,
        success=success,
        meeting=meeting,
        state_cities=state_cities,
        selected_state=selected_state,
        city_list=city_list
    )


@app.route('/track_user')
def track_user():
    if session.get('role') != 'user':
        return redirect(url_for('login'))
    app_id = session.get('application_id')
    if not app_id:
        return redirect(url_for('login'))
    app = applications.get(app_id)
    meetup = meetings.get(app_id)
    return render_template('track_user.html', app_id=app_id, app=app, meetup=meetup)

@app.route('/track_admin')
def track_admin():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

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

@app.route('/delete-meeting/<app_id>', methods=['GET'])
def delete_meeting(app_id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    # Delete meeting if exists
    if app_id in meetings:
        del meetings[app_id]

    # Delete application if exists
    if app_id in applications:
        del applications[app_id]

    return redirect(url_for('track_admin'))


@app.route('/submit_review', methods=['POST'])
def submit_review():
    app_id = request.form.get('application_id')
    feedback = request.form.get('feedback', '')

    if app_id in applications and applications[app_id]['finalized']:
        applications[app_id]['review'] = {
            'by': app_id,
            'feedback': feedback
        }

    return redirect(url_for('track_admin' if session.get('role') == 'admin' else 'track_user'))

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

    return render_template(
        'edit_meeting.html',
        app_id=app_id,
        meeting=meetings.get(app_id),
        error=error,
        success=success,
        state_cities=state_cities,
        selected_state=selected_state,
        city_list=city_list,
    )

@app.route('/dashboard')
def dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)