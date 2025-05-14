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

    # Drop and recreate for resetting data during development
    c.execute("DROP TABLE IF EXISTS users")

    # Create updated info table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            fullname TEXT,
            dob TEXT,
            gender TEXT,
            nationality TEXT,
            language TEXT,
            bio TEXT,
            profile_pic TEXT
            primary_address TEXT,
            shipping_address TEXT
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

def update_password(username, new_password):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username))
    conn.commit()
    conn.close()

# save personal information    
def update_personal_info(username, fullname, dob, gender, nationality, language, bio, profile_pic):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("""
        UPDATE users SET 
            fullname = ?, dob = ?, gender = ?, nationality = ?, 
            language = ?, bio = ?, profile_pic = ?
        WHERE username = ?
    """, (fullname, dob, gender, nationality, language, bio, profile_pic, username))
    conn.commit()
    conn.close()

# save contact information
def update_contact_info(username, primary_address, shipping_address):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("""
        UPDATE users SET
            primary_address = ?, shipping_address = ?
        WHERE username = ?
    """, (primary_address, shipping_address, username))
    conn.commit()
    conn.close()