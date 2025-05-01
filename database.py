import sqlite3

def init_db():
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()

    # create user table (if not exist) storing usernames and passwords
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )""")

    # create tasks table (if not exist) storing tasks associated with users
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

# add new user to database
def add_user(username, password):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

# get user from database (for login purposes)
def get_user(username, password):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()
    conn.close()
    return user

# add task to database, associated with user
def add_task(username, task, date):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("INSERT INTO tasks (username, task, date) VALUES (?, ?, ?)", (username, task, date))
    conn.commit()
    conn.close()

# get all tasks from database
def get_tasks():
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("SELECT username, task, date FROM tasks")
    tasks = c.fetchall()
    conn.close()
    return tasks

# add hardcoded user and task if database is empty
def add_hardcoded_data():
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    
    # check if 'users' table is empty
    c.execute("SELECT COUNT(*) FROM users")
    user_count = c.fetchone()[0]

    if user_count == 0:
        # add hardcoded user
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "1234"))
        conn.commit()

    # check if there are any tasks
    c.execute("SELECT COUNT(*) FROM tasks")
    task_count = c.fetchone()[0]

    if task_count == 0:
        # add hardcoded tasks for admin user
        c.execute("INSERT INTO tasks (username, task, date) VALUES (?, ?, ?)", ("admin", "Feed the dog", "2025-05-01"))
        c.execute("INSERT INTO tasks (username, task, date) VALUES (?, ?, ?)", ("admin", "Clean the cage", "2025-05-01"))
        conn.commit()
    conn.close()