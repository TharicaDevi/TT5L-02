import sqlite3

conn = sqlite3.connect("pets.db")
c = conn.cursor()

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

def add_pet(name, picture, type_, color, breed, age, status="available"):
    conn = sqlite3.connect("pets.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO pets (name, picture, type, color, breed, age, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, picture, type_, color, breed, age, status))
    conn.commit()
    conn.close()


add_pet("Milo", "dog1.jpeg", "Dog", "Golden", "Golden Retriever", 1, "available")
add_pet("Snowy", "cat1.jpeg", "Cat", "White", "Persian", 2, "available")
add_pet("Hammy", "hamster1.jpeg", "Hamster", "Brown", "Roborovski Dwarf", 2, "available")
add_pet("Oyen", "cat2.jpeg", "Cat", "Orange", "Persian", 4, "available")
add_pet("Xixi", "cat3.jpeg", "Cat", "Grey", "Persian", 1, "available")
add_pet("Spike", "dog2.jpeg", "Dog", "Calico", "Chihuahua", 3, "available")
add_pet("Tabby", "cat4.jpeg", "Cat", "Seal point", "Siamese", 1, "available")
add_pet("Sam", "hamster2.jpeg", "Hamster", "Orange", "Syrian hamster", 1, "available")
