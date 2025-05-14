import sqlite3

# Initialize all tables
def init_db():
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()

    # USERS table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    # PETS table
    c.execute("""
        CREATE TABLE IF NOT EXISTS pets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            picture TEXT,
            type TEXT NOT NULL,
            color TEXT NOT NULL,
            breed TEXT NOT NULL,
            age INTEGER NOT NULL,
            status TEXT NOT NULL
        )
    """)

    # ADOPTIONS table
    c.execute("""
        CREATE TABLE IF NOT EXISTS adoptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            pet_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (pet_id) REFERENCES pets(id)
        )
    """)

    # MEETINGS table
    c.execute("""
        CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()

# Add a new user
def add_user(username, password, email, phone, status):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO users (username, password, email, phone, status)
        VALUES (?, ?, ?, ?, ?)
    """, (username, password, email, phone, status))
    conn.commit()
    conn.close()

# Add a new pet
def add_pet(picture, type_, color, breed, age, status):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO pets (picture, type, color, breed, age, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (picture, type_, color, breed, age, status))
    conn.commit()
    conn.close()

# Add a new adoption request
def add_adoption(user_id, pet_id, status):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO adoptions (user_id, pet_id, status)
        VALUES (?, ?, ?)
    """, (user_id, pet_id, status))
    conn.commit()
    conn.close()

# Schedule a new meeting
def schedule_meeting(user_id, date, time, notes):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO meetings (user_id, date, time, notes)
        VALUES (?, ?, ?, ?)
    """, (user_id, date, time, notes))
    conn.commit()
    conn.close()

# Get all pets
def get_all_pets():
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("SELECT * FROM pets")
    pets = c.fetchall()
    conn.close()
    return pets

# Get all adoptions with user and pet details
def get_adoptions():
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("""
        SELECT adoptions.id, users.username, pets.type, adoptions.status
        FROM adoptions
        JOIN users ON adoptions.user_id = users.id
        JOIN pets ON adoptions.pet_id = pets.id
    """)
    records = c.fetchall()
    conn.close()
    return records
