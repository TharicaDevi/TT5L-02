import sqlite3
from datetime import datetime

# Initialize the database and all required tables
def init_db():
    conn = sqlite3.connect("pets.db")
    c = conn.cursor()

    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT,
            email TEXT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            status TEXT
        )
    """)

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

     # Adoption requests table
    c.execute('''
        CREATE TABLE IF NOT EXISTS adoption_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            pet_id INTEGER NOT NULL,
            request_date TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            message TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(pet_id) REFERENCES pets(id)
        )
    ''')

    conn.commit()
    conn.close()

def add_user(phone, email, username, password, status="active"):
    conn = sqlite3.connect("pets.db")
    c = conn.cursor()
    c.execute("INSERT INTO users (phone, email, username, password, status) VALUES (?, ?, ?, ?, ?)",
              (phone, email, username, password, status))
    conn.commit()
    conn.close()

def get_user_by_credentials(username, password):
    conn = sqlite3.connect("pets.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()
    conn.close()
    return user

def add_pet(picture, type_, color, breed, age, status="available"):
    conn = sqlite3.connect("pets.db")
    c = conn.cursor()
    c.execute("INSERT INTO pets (picture, type, color, breed, age, status) VALUES (?, ?, ?, ?, ?, ?)",
              (picture, type_, color, breed, age, status))
    conn.commit()
    conn.close()

def get_all_pets():
    conn = sqlite3.connect("pets.db")
    c = conn.cursor()
    c.execute("SELECT * FROM pets WHERE status = 'available'")
    pets = c.fetchall()
    conn.close()
    return pets

def get_pet_by_id(pet_id):
    conn = sqlite3.connect("pets.db")
    c = conn.cursor()
    c.execute("SELECT * FROM pets WHERE id = ?", (pet_id,))
    pet = c.fetchone()
    conn.close()
    return pet

def filter_pets(breed=None, age=None):
    conn = sqlite3.connect("pets.db")
    c = conn.cursor()
    query = "SELECT * FROM pets WHERE status = 'available'"
    params = []
    if breed:
        query += " AND breed = ?"
        params.append(breed)
    if age:
        query += " AND age = ?"
        params.append(int(age))
    c.execute(query, params)
    pets = c.fetchall()
    conn.close()
    return pets

def add_adoption(user_id, pet_id, status="pending"):
    conn = sqlite3.connect("pets.db")
    c = conn.cursor()
    c.execute("INSERT INTO adoptions (user_id, pet_id, status) VALUES (?, ?, ?)",
              (user_id, pet_id, status))
    conn.commit()
    conn.close()

def get_adoption_status(user_id):
    conn = sqlite3.connect("pets.db")
    c = conn.cursor()
    c.execute("SELECT * FROM adoptions WHERE user_id = ?", (user_id,))
    adoptions = c.fetchall()
    conn.close()
    return adoptions

def schedule_meeting(user_id, date, time, notes):
    conn = sqlite3.connect("pets.db")
    c = conn.cursor()
    c.execute("INSERT INTO meetings (user_id, date, time, notes) VALUES (?, ?, ?, ?)",
              (user_id, date, time, notes))
    conn.commit()
    conn.close()

def get_meetings_by_user(user_id):
    conn = sqlite3.connect("pets.db")
    c = conn.cursor()
    c.execute("SELECT * FROM meetings WHERE user_id = ?", (user_id,))
    meetings = c.fetchall()
    conn.close()
    return meetings

def add_adoption_request(user_id, pet_id, message=""):
    conn = sqlite3.connect('pets.db')
    c = conn.cursor()
    
    request_date = datetime.now().strftime("%Y-%m-%d")
    c.execute('''
        INSERT INTO adoption_requests (user_id, pet_id, request_date, message)
        VALUES (?, ?, ?, ?)
    ''', (user_id, pet_id, request_date, message))
    
    conn.commit()
    conn.close()

def get_all_adoption_requests():
    conn = sqlite3.connect('pets.db')
    c = conn.cursor()

    c.execute('''
        SELECT ar.id, ar.user_id, ar.pet_id, ar.request_date, ar.status, ar.message,
               u.username, p.name
        FROM adoption_requests ar
        JOIN users u ON ar.user_id = u.id
        JOIN pets p ON ar.pet_id = p.id
    ''')
    
    requests = c.fetchall()
    conn.close()
    return requests