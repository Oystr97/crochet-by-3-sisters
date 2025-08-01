import sqlite3

conn = sqlite3.connect("products.db")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS products")

cursor.execute("""
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price_inr REAL NOT NULL,
    price_gbp REAL NOT NULL,
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
    video TEXT,
    rating REAL DEFAULT 0,
    rating_count INTEGER DEFAULT 0
)
""")

conn.commit()
conn.close()

print("✅ products table created successfully.")
