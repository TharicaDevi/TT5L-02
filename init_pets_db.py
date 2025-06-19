import sqlite3

def init_pets_db():
    conn = sqlite3.connect("pets.db")
    c = conn.cursor()

    # Create pets table if not exists
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
    print("✅ pets.db is ready with the pets table.")

# Call it
init_pets_db()
