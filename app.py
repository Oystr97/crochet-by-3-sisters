from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# === File Upload Configuration ===
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# === Database Connections ===
def get_products_db_connection():
    conn = sqlite3.connect('products.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_users_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

# === Routes ===

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/select_country', methods=['POST'])
def select_country():
    session['country'] = request.form['country']
    return redirect('/')

@app.route('/category/<category>')
def category(category):
    conn = get_products_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE category = ?", (category,))
    products = cursor.fetchall()
    conn.close()
    return render_template('category.html', products=products, category=category)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    conn = get_products_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    conn.close()
    return render_template('product_detail.html', product=product)

@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if 'cart' not in session:
        session['cart'] = []

    conn = get_products_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        product_id = int(request.form['product_id'])
        quantity = int(request.form['quantity'])
        found = False
        for item in session['cart']:
            if item['product_id'] == product_id:
                item['quantity'] = quantity
                found = True
                break
        if not found:
            session['cart'].append({'product_id': product_id, 'quantity': quantity})
        flash("Cart updated!")
        return redirect('/cart')

    cart_items = []
    total = 0
    country = session.get('country', 'IN')

    for item in session['cart']:
        cursor.execute("SELECT * FROM products WHERE id = ?", (item['product_id'],))
        product = cursor.fetchone()
        if product:
            price = product['price_in'] if country == 'IN' else product['price_uk']
            subtotal = price * item['quantity']
            total += subtotal
            cart_items.append({
                'product': product,
                'quantity': item['quantity'],
                'subtotal': subtotal
            })

    conn.close()
    return render_template('cart.html', cart_items=cart_items, total=total, country=country)

@app.route('/checkout', methods=['POST'])
def checkout():
    session['cart'] = []
    flash("Order placed successfully!")
    return redirect('/')

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    country = session.get('country', 'IN')
    total = float(request.args.get('total', 0))
    return render_template('payment.html', country=country, total=total)

# === New Product Upload Route ===
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        price_inr = float(request.form['price_inr'])
        price_gbp = float(request.form['price_gbp'])
        length = request.form.get('length')
        height = request.form.get('height')
        width = request.form.get('width')
        weight = request.form.get('weight')
        material = request.form.get('material')
        description = request.form['description']

        images = request.files.getlist('images')
        video = request.files.get('video')

        image_paths = []
        for image in images:
            if image.filename != '':
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_paths.append(filename)

        video_filename = None
        if video and video.filename != '':
            video_filename = secure_filename(video.filename)
            video.save(os.path.join(app.config['UPLOAD_FOLDER'], video_filename))

        conn = get_products_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO products
            (name, category, price_in, price_uk, description, length, height, width, weight, material,
             image1, image2, image3, image4, video)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            name, category, price_inr, price_gbp, description,
            length, height, width, weight, material,
            image_paths[0] if len(image_paths) > 0 else None,
            image_paths[1] if len(image_paths) > 1 else None,
            image_paths[2] if len(image_paths) > 2 else None,
            image_paths[3] if len(image_paths) > 3 else None,
            video_filename
        ))
        conn.commit()
        conn.close()

        flash("✅ Product added successfully!")
        return redirect('/add_product')

    return render_template('add_product.html')

# === Run the app ===
if __name__ == '__main__':
    app.run(debug=True)
