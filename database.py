import sqlite3

# Initialize the database and create tables if they don't exist
def init_db():
    conn = sqlite3.connect("info.db")
    c = conn.cursor()

    # Drop and recreate for resetting data during development
    c.execute("DROP TABLE IF EXISTS users")
    c.execute("DROP TABLE IF EXISTS accounts")
    c.execute("DROP TABLE IF EXISTS profiles")
    c.execute("DROP TABLE IF EXISTS addresses")
    c.execute("DROP TABLE IF EXISTS privacy")
    c.execute("DROP TABLE IF EXISTS security")

    # user table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # accounts table
    c.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            pending_email TEXT,
            email_verified INTEGER DEFAULT 1,
            phone TEXT
        )
    """)     

    # profiles table
    c.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            user_id INTEGER PRIMARY KEY,
            fullname TEXT,
            dob TEXT,
            gender TEXT,
            nationality TEXT,
            language TEXT,
            bio TEXT,
            profile_pic TEXT,
            FOREIGN KEY (user_id) REFERENCES accounts(id) ON DELETE CASCADE
        );
    """)

    # addresses table
    c.execute("""
        CREATE TABLE IF NOT EXISTS addresses (
            user_id INTEGER PRIMARY KEY,
            primary_address TEXT,
            shipping_address TEXT,
            FOREIGN KEY (user_id) REFERENCES accounts(id) ON DELETE CASCADE
        );
    """)

    # privacy table
    c.execute("""
        CREATE TABLE IF NOT EXISTS privacy (
            user_id INTEGER PRIMARY KEY,
            visibility TEXT DEFAULT 'public',
            activity_status TEXT DEFAULT 'show',
            FOREIGN KEY (user_id) REFERENCES accounts(id) ON DELETE CASCADE
        );
    """)

    # security table
    c.execute("""
        CREATE TABLE IF NOT EXISTS security (
            user_id INTEGER PRIMARY KEY,
            security_question TEXT,
            security_answer TEXT,
            FOREIGN KEY (user_id) REFERENCES accounts(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()

# Add a new user to the users table
def add_user(username, password):
    conn = sqlite3.connect("info.db")
    c = conn.cursor()

    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    c.execute("INSERT INTO accounts (username, password) VALUES (?, ?)", (username, password))
    account_id = c.lastrowid
    c.execute("INSERT INTO profiles (user_id) VALUES (?)", (account_id,))
    c.execute("INSERT INTO addresses (user_id) VALUES (?)", (account_id,))
    c.execute("INSERT INTO privacy (user_id) VALUES (?)", (account_id,))
    c.execute("INSERT INTO security (user_id) VALUES (?)", (account_id,))
    conn.commit()
    conn.close()

# Get a user from the database (for login validation)
def get_user(username, password):
    conn = sqlite3.connect("info.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()
    conn.close()
    return user

# Check if a username already exists
def user_exists(username):
    conn = sqlite3.connect("info.db")
    c = conn.cursor()
    c.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    return result is not None

def update_password(username, new_password):
    conn = sqlite3.connect("info.db")
    c = conn.cursor()
    c.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username))
    conn.commit()
    conn.close()

def get_user_by_username(username):
    conn = sqlite3.connect("info.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_account_id(username):
    conn = sqlite3.connect("info.db")
    c = conn.cursor()
    c.execute("SELECT id FROM accounts WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

# save account information
def update_account_info(username, email, phone, password):
    conn = sqlite3.connect("info.db")
    cursor = conn.cursor()

    if email:
        cursor.execute("UPDATE accounts SET pending_email = ?, email_verified = 0 WHERE username = ?", (email, username))
    if phone:
        cursor.execute("UPDATE accounts SET phone = ? WHERE username = ?", (phone, username))
    if password:
        cursor.execute("UPDATE accounts SET password = ? WHERE username = ?", (password, username))
    conn.commit()
    conn.close()

def verify_pending_email(username):
    conn = sqlite3.connect("info.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE accounts SET email = pending_email, pending_email = NULL, email_verified = 1 WHERE username = ?", (username,))
    conn.commit()
    conn.close()

# save personal information    
def update_personal_info(username, fullname, dob, gender, nationality, language, bio, profile_pic):
    user_id = get_account_id(username)
    conn = sqlite3.connect("info.db")
    c = conn.cursor()

    c.execute("""
        UPDATE profiles SET 
            fullname = ?, dob = ?, gender = ?, nationality = ?, 
            language = ?, bio = ?, profile_pic = ?
        WHERE user_id = ?
    """, (fullname, dob, gender, nationality, language, bio, profile_pic, user_id))
    conn.commit()
    conn.close()

def get_personal_info(username):
    user_id = get_account_id(username)
    conn = sqlite3.connect("info.db")
    c = conn.cursor()

    c.execute("""
              SELECT fullname, dob, gender, nationality, language, bio, profile_pic 
              FROM profiles WHERE user_id = ?
    """, (user_id,))

    row = c.fetchone()
    conn.close()
    return row

# save contact information
def update_contact_info(username, primary_address, shipping_address):
    user_id = get_account_id(username)
    conn = sqlite3.connect("info.db")
    c = conn.cursor()
    c.execute("""
        UPDATE addresses SET
            primary_address = ?, shipping_address = ?
        WHERE user_id = ?
    """, (primary_address, shipping_address, user_id))
    conn.commit()
    conn.close()

# save privacy settings
def update_privacy_settings(username, visibility, activity_status):
    user_id = get_account_id(username)
    conn = sqlite3.connect("info.db")
    c = conn.cursor()
    c.execute("""
        UPDATE privacy SET
            visibility = ?, activity_status = ?
        WHERE user_id = ?
    """, (visibility, activity_status, user_id))
    conn.commit()
    conn.close()

def get_privacy_settings(username):
    conn = sqlite3.connect("info.db")
    c = conn.cursor()
    user_id = get_account_id(username)
    c.execute("SELECT visibility, activity_status FROM privacy WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result

# save security question & answer
def update_security_settings(username, question, answer):
    user_id = get_account_id(username)
    conn = sqlite3.connect("info.db")
    c = conn.cursor()
    c.execute("""
        UPDATE security SET
            security_question = ?, security_answer = ?
        WHERE user_id = ?
    """, (question, answer, user_id))
    conn.commit()
    conn.close()

# delete account
def delete_account(username):
    conn = sqlite3.connect("info.db")
    c = conn.cursor()
    c.execute("DELETE FROM accounts WHERE username = ?", (username,))
    conn.commit()
    conn.close()