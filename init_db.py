import sqlite3

conn = sqlite3.connect('database.db')  # or whatever your DB is called
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    length REAL,
    height REAL,
    width REAL,
    weight REAL,
    material TEXT,
    image1 TEXT,
    image2 TEXT,
    image3 TEXT,
    image4 TEXT,
    rating INTEGER DEFAULT 0
)
''')

conn.commit()
conn.close()

print("✅ Database and products table created.")
