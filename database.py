import sqlite3, smtplib
from email.message import EmailMessage

EMAIL_ADDRESS = "pawfecthome4u@gmail.com"
EMAIL_PASSWORD = "cioc tkda ykzw chrd"

with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()
    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    
# Initialize the database and create tables if they don't exist
def init_info_db():
    conn = sqlite3.connect("info.db")
    c = conn.cursor()

    # Drop and recreate for resetting data during development
    c.execute("DROP TABLE IF EXISTS users")

    # Create updated info table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            fullname TEXT,
            dob TEXT,
            gender TEXT,
            nationality TEXT,
            language TEXT,
            bio TEXT,
            primary_address TEXT,
            shipping_address TEXT,
            visibility TEXT DEFAULT 'public',
            activity_status TEXT DEFAULT 'show'
        )
    """)

    conn.commit()
    conn.close()

def init_pets_db():
    conn = sqlite3.connect("pets.db")
    c = conn.cursor()

    # Pets table
    c.execute("""
        CREATE TABLE IF NOT EXISTS pets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            picture TEXT,
            type TEXT,
            color TEXT,
            breed TEXT,
            age INTEGER,
            status TEXT
        )
    """)

    conn.commit()
    conn.close()

def init_adoptions_db():
    conn = sqlite3.connect("adoptions.db")
    c = conn.cursor()

    # Adoptions table
    c.execute("""
        CREATE TABLE IF NOT EXISTS adoptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            pet_id INTEGER,
            status TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (pet_id) REFERENCES pets(id)
        )
    """)

    # Meetings table
    c.execute("""
        CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT,
            time TEXT,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()

# Add a new user to the users table
def add_user(username, password, email):
    conn = sqlite3.connect("info.db")
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", (username, password, email))
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

# Check if email already registered
def email_exists(email):
    conn = sqlite3.connect("info.db")
    c = conn.cursor()
    c.execute("SELECT 1 FROM users WHERE email = ?", (email,))
    result = c.fetchone()
    conn.close()
    return result is not None

def update_password(username, new_password):
    conn = sqlite3.connect("info.db")
    c = conn.cursor()
    c.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username))
    conn.commit()
    conn.close()

def update_password_by_email(email, new_password):
    conn = sqlite3.connect("info.db")
    c = conn.cursor()
    c.execute("UPDATE users SET password = ? WHERE email = ?", (new_password, email))
    conn.commit()
    conn.close()

def send_otp_email(recipient_email, otp):
    msg = EmailMessage()
    msg['Subject'] = "Your OTP Code"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = recipient_email
    msg.set_content(f"Your OTP code is: {otp}")

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

def validate_username_email(username, email):
    conn = sqlite3.connect('info.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND email=?", (username, email))
    result = c.fetchone()
    conn.close()
    return result is not None

def get_user_by_username(username):
    conn = sqlite3.connect("info.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_email(email):
    conn = sqlite3.connect("info.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()
    return user

# save account information
def update_account_info(username, email, phone):
    conn = sqlite3.connect("info.db")
    cursor = conn.cursor()

    if email:
        cursor.execute("UPDATE users SET email = ? WHERE username = ?", (email, username))
    if phone:
        cursor.execute("UPDATE users SET phone = ? WHERE username = ?", (phone, username))
    conn.commit()
    conn.close()

# save personal information    
def update_personal_info(username, fullname, dob, gender, nationality, language, bio):
    conn = sqlite3.connect("info.db")
    c = conn.cursor()
    c.execute("""
        UPDATE users SET 
            fullname = ?, dob = ?, gender = ?, nationality = ?, 
            language = ?, bio = ?
        WHERE username = ?
    """, (fullname, dob, gender, nationality, language, bio, username))
    conn.commit()
    conn.close()

def get_personal_info(username):
    conn = sqlite3.connect("info.db")
    c = conn.cursor()
    c.execute("SELECT fullname, dob, gender, nationality, language, bio, profile_pic FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    return row

# save contact information
def update_contact_info(username, primary_address, shipping_address):
    conn = sqlite3.connect("info.db")
    c = conn.cursor()
    c.execute("""
        UPDATE users SET
            primary_address = ?, shipping_address = ?
        WHERE username = ?
    """, (primary_address, shipping_address, username))
    conn.commit()
    conn.close()

# save privacy settings
def update_privacy_settings(username, visibility, activity_status):
    conn = sqlite3.connect("info.db")
    c = conn.cursor()
    c.execute("""
        UPDATE users SET
            visibility = ?, activity_status = ?
        WHERE username = ?
    """, (visibility, activity_status, username))
    conn.commit()
    conn.close()

def get_privacy_settings(username):
    conn = sqlite3.connect("info.db")
    c = conn.cursor()
    c.execute("SELECT visibility, activity_status FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    return result

# delete account
def delete_account(username):
    conn = sqlite3.connect("info.db")
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()

# schedule meeting
def schedule_meeting(user_id, date, time, notes):
    conn = sqlite3.connect("adoptions.db")
    c = conn.cursor()
    c.execute("INSERT INTO meetings (user_id, date, time, notes) VALUES (?, ?, ?, ?)",
              (user_id, date, time, notes))
    conn.commit()
    conn.close()

def get_meetings_by_user(user_id):
    conn = sqlite3.connect("adoptions.db")
    c = conn.cursor()
    c.execute("SELECT * FROM meetings WHERE user_id = ?", (user_id,))
    meetings = c.fetchall()
    conn.close()
    return meetings

# admin -> insert pet
def insert_pet(name, picture, pet_type, color, breed, age, status):
    try:
        conn = sqlite3.connect('pets.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO pets (name, picture, type, color, breed, age, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, picture, pet_type, color, breed, age, status))
        conn.commit()
        return c.lastrowid
    except Exception as e:
        print("Error inserting pet:", e)
        return None
    finally:
        conn.close()

def get_all_pets():
    conn = sqlite3.connect("pets.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM pets WHERE status = 'available'")
    pets = c.fetchall()
    conn.close()
    return pets

def get_pet_by_id(pet_id):
    conn = sqlite3.connect("pets.db")
    conn.row_factory = sqlite3.Row  
    c = conn.cursor()
    c.execute("SELECT * FROM pets WHERE id = ?", (pet_id,))
    pet = c.fetchone()
    conn.close()
    return pet

def filter_pets(breed):
    conn = sqlite3.connect('pets.db') 
    c = conn.cursor()

    breed = breed.lower()
    query = '''
        SELECT * FROM pets
        WHERE LOWER(breed) LIKE ?
    '''
    c.execute(query, (f"%{breed}%",))
    pets = c.fetchall()
    conn.close()
    return pets