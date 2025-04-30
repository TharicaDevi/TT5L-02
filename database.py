import sqlite3

def init_db():
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT,
            task TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def add_user_table():
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()

    # Create the users table if it doesn't already exist
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    print("✅ 'users' table created successfully.")

add_user_table()

def add_task(username, password, task):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password, task) VALUES (?, ?, ?)", (username, password, task))
    conn.commit()
    conn.close()

def get_tasks(username):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("SELECT task FROM users WHERE username = ?", (username,))
    tasks = c.fetchall()
    conn.close()
    return tasks

if __name__ == "__main__":
    init_db()
    add_task("admin", "1234", "Feed the dog") #hardcoded
    add_task("admin", "1234", "Clean the cage")

    print("Tasks for admin:")
    for task in get_tasks("admin"):
        print("-", task[0])

 