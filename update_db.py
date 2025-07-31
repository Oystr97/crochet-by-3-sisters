import sqlite3

conn = sqlite3.connect('products.db')
cursor = conn.cursor()

# Add INR and UK price columns to existing products table
cursor.execute("ALTER TABLE products ADD COLUMN price_in REAL")
cursor.execute("ALTER TABLE products ADD COLUMN price_uk REAL")

conn.commit()
conn.close()
print("✅ Added price_in and price_uk to products table.")

