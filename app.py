from flask import Flask, render_template, request, redirect, session, flash, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ✅ Create uploads folder if it doesn't exist
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ✅ Separate DB connection functions
def get_users_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_products_db_connection():
    conn = sqlite3.connect('products.db')
    conn.row_factory = sqlite3.Row
    return conn

# ✅ Product Upload Route
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        price_in = float(request.form['price_inr'])
        price_uk = float(request.form['price_gbp'])
        description = request.form['description']
        length = request.form.get('length')
        height = request.form.get('height')
        width = request.form.get('width')
        weight = request.form.get('weight')
        material = request.form.get('material')

        # ✅ Handle multiple images
        images = request.files.getlist('images')
        image_paths = []
        for image in images[:4]:
            if image.filename != '':
                save_path = os.path.join(UPLOAD_FOLDER, image.filename)
                image.save(save_path)
                image_paths.append(save_path)

        # Pad with empty strings
        while len(image_paths) < 4:
            image_paths.append("")

        conn = get_products_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO products 
            (name, price_in, price_uk, category, description, length, height, width, weight, material, image1, image2, image3, image4)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            name, price_in, price_uk, category, description, length, height, width, weight, material,
            image_paths[0], image_paths[1], image_paths[2], image_paths[3]
        ))
        conn.commit()
        conn.close()
        return "✅ Product added successfully!"

    return render_template("add_product.html")
