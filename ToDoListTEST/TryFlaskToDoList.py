from flask import Flask, render_template, request, redirect, session, url_for, g
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this in production

# Database setup
DATABASE = 'todo.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db:
        db.close()

# Create tables if not exist
with app.app_context():
    db = get_db()
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    db.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            task TEXT NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    db.commit()

# ROUTES
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('todo'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        try:
            db.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            db.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "Username already exists."
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('todo'))
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/todo', methods=['GET', 'POST'])
def todo():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db()
    if request.method == 'POST':
        task = request.form['task']
        date = request.form['date']
        db.execute("INSERT INTO tasks (user_id, task, date) VALUES (?, ?, ?)", (session['user_id'], task, date))
        db.commit()
        return redirect(url_for('todo'))

    tasks = db.execute("SELECT task, date FROM tasks WHERE user_id = ?", (session['user_id'],)).fetchall()
    return render_template('todo.html', username=session['username'], tasks=tasks)

if __name__ == '__main__':
    app.run(debug=True)
