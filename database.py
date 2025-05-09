import sqlite3

# Initialize the database and create tables if they don't exist
def init_db():
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()

    # Create user table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Create tasks table
    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            task TEXT NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    """)

    conn.commit()
    conn.close()

# Add a new user to the users table
def add_user(username, password):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

# Get a user from the database (for login validation)
def get_user(username, password):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()
    conn.close()
    return user

# Check if a username already exists
def user_exists(username):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    return result is not None

# Add a new task to the tasks table
def add_task(username, task, date):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("INSERT INTO tasks (username, task, date) VALUES (?, ?, ?)", (username, task, date))
    conn.commit()
    conn.close()

# Get all tasks from the tasks table 
def get_tasks():
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("SELECT username, task, date FROM tasks")
    tasks = c.fetchall()
    conn.close()
    return tasks