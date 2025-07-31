import gspread
import sqlite3
from oauth2client.service_account import ServiceAccountCredentials

# 1. Set up Google Sheets credentials
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# 2. Open your Google Sheet
sheet = client.open("Product listing for Crochet by 3 Sisters").sheet1

# 3. Fetch all rows
rows = sheet.get_all_values()
header = rows[0]
data_rows = rows[1:]

# 4. Connect to SQLite
conn = sqlite3.connect("products.db")
cursor = conn.cursor()

# 5. Loop through sheet rows
for row in data_rows:
    if len(row) < 16:
        continue  # skip incomplete

    (
        name, price_inr, price_gbp, category, description, length, height,
        width, weight, material, image1, image2, image3, image4, video
    ) = row[1:16]

    # Check for duplicates (same name + category)
    cursor.execute("SELECT COUNT(*) FROM products WHERE name = ? AND category = ?", (name, category))
    if cursor.fetchone()[0] > 0:
        continue  # already uploaded

    # Insert product
    cursor.execute("""
        INSERT INTO products (
            name, price_inr, price_gbp, category, description,
            length, height, width, weight, material,
            image1, image2, image3, image4, video,
            rating, rating_count
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name, price_inr, price_gbp, category, description,
        length, height, width, weight, material,
        image1, image2, image3, image4, video,
        0, 0  # default rating and count
    ))

conn.commit()
conn.close()
print("✅ Upload complete.")
