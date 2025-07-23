import sqlite3

conn = sqlite3.connect('products.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,
    name TEXT,
    price REAL,
    images TEXT,
    video TEXT,
    length TEXT,
    height TEXT,
    width TEXT,
    weight TEXT,
    material TEXT,
    description TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    stars INTEGER CHECK(stars BETWEEN 1 AND 5)
)
''')

conn.commit()
conn.close()
print("✅ Product and ratings tables created.")
