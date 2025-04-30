from flask import Flask, request, redirect, url_for, session, flash, render_template
import sqlite3

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # needed for session (session = store information about the user across multiple pages)

DATABASE = 'tasks.db'

# function to connect to database
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    if 'user' in session:
        return f"Hello, {session['user']}! <a href='/logout'>Logout</a><br><a href='/add'>Go to Add Task</a>"
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST']) # get=view, post=submit
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('pw')

        conn = get_db()
        cursor = conn.cursor()
        
        # check if username exists
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()

        if not user:
            flash('User not found.', 'danger')
        elif user['password'] != password:
            flash('Wrong password.', 'danger')
        else:
            session['user'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('home'))

        conn.close()

    return render_template('login.html')