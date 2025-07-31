import sqlite3

conn = sqlite3.connect('products.db')
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(products)")
for column in cursor.fetchall():
    print(column)

conn.close()
