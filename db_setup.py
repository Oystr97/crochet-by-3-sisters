import sqlite3

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        contact TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        address TEXT,
        password TEXT NOT NULL
    )
''')

conn.commit()
conn.close()
print("✅ SQLite database and 'users' table created successfully!")
