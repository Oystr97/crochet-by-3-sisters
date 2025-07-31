import sqlite3

# Connect to (or create) a new database file
conn = sqlite3.connect('products.db')
cursor = conn.cursor()

# Read the SQL file
with open('init_products.sql', 'r') as f:
    sql = f.read()

# Execute the SQL commands
cursor.executescript(sql)

# Commit changes and close connection
conn.commit()
conn.close()

print("✅ Database created successfully!")
