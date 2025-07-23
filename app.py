# Updated app.py with country-based pricing support
from flask import Flask, render_template, request, redirect, session, flash, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ✅ Reusable DB connection function
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

# ✅ Route to set selected country
@app.route('/set_country', methods=['POST'])
def set_country():
    selected_country = request.form.get('country')
    if selected_country:
        session['country'] = selected_country
    return redirect(request.referrer or url_for('home'))

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/makers')
def makers():
    return render_template("makers.html")

@app.route('/<category>')
def show_products(category):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE category = ?", (category.lower(),))
    products = cursor.fetchall()
    conn.close()

    user_country = session.get('country', 'India')

    for product in products:
        if user_country == 'UK':
            product['display_price'] = f"£ {product['price_uk']:.2f}"
        else:
            product['display_price'] = f"₹ {product['price_in']:.2f}"

    return render_template("product_list.html", category=category.title(), products=products)

# ✅ SIGNUP route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        contact = request.form['contact']
        email = request.form['email']
        address = request.form['address']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ? OR contact = ?', (email, contact))
        user = cursor.fetchone()

        if user:
            flash("Account already exists. Please login or reset your password.")
            return redirect('/signup')
        else:
            hashed_password = generate_password_hash(password)
            cursor.execute(
                'INSERT INTO users (name, contact, email, address, password) VALUES (?, ?, ?, ?, ?)',
                (name, contact, email, address, hashed_password)
            )
            conn.commit()
            conn.close()

            session['user'] = email
            return redirect('/')

    return render_template("signup.html")

# ✅ LOGIN route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form['identifier']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ? OR contact = ?', (identifier, identifier))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user'] = user['email']
            return redirect('/')
        else:
            flash('Invalid credentials. Try again or reset your password.')
            return redirect('/login')

    return render_template('login.html')

# ✅ ADD TO CART
@app.route('/add_to_cart', methods=["POST"])
def add_to_cart():
    user_country = session.get('country', 'India')
    name = request.form["name"]
    quantity = int(request.form["quantity"])
    price = float(request.form["price_in"] if user_country == 'India' else request.form["price_uk"])

    item = {"name": name, "price": price, "quantity": quantity}

    if 'cart' not in session:
        session['cart'] = []

    cart = session['cart']
    cart.append(item)
    session['cart'] = cart

    return redirect('/cart')

@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    country = session.get('country', 'India')

    total = 0
    for item in cart:
        item['display_price'] = item['price_inr'] if country == 'India' else item['price_gbp']
        total += item['display_price'] * item['quantity']

    return render_template("cart.html", cart=cart, total=total, country=country)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/update_cart', methods=['POST'])
def update_cart():
    cart = session.get('cart', [])
    quantity_updates = request.form.getlist('quantities')

    for item_update in quantity_updates:
        index, new_qty = map(int, item_update.split('-'))
        cart[index]['quantity'] = new_qty

    session['cart'] = cart
    return redirect('/cart')

@app.route('/checkout_address', methods=['GET', 'POST'])
def checkout_address():
    if request.method == 'POST':
        session['order_details'] = {
            "name": request.form['name'],
            "address": request.form['address'],
            "contact": request.form['contact']
        }
        return redirect('/payment')

    conn = get_db_connection()
    user_email = session.get('user')
    user_data = conn.execute('SELECT * FROM users WHERE email = ?', (user_email,)).fetchone()
    conn.close()

    return render_template('checkout_address.html', user=user_data)

@app.route('/payment')
def payment():
    country = session.get('country', 'India')
    cart = session.get('cart', [])
    total = 0
    for item in cart:
        price = item['price_inr'] if country == 'India' else item['price_gbp']
        total += price * item['quantity']
    return render_template("payment.html", total=total, country=country)

@app.route('/payment_success', methods=['POST'])
def payment_success():
    txn_id = request.form['upi_txn']
    if not txn_id.strip():
        return redirect('/payment_fail')

    import time
    order_id = f"ORD{int(time.time())}"
    cart = session.get('cart', [])
    customer = session.get('order_details')
    user_email = session.get('user')

    send_order_email(user_email, order_id, cart, customer)
    send_order_email("kalpanamore1000@gmail.com", order_id, cart, customer)

    session.pop('cart', None)
    session['show_thank_you'] = True
    return redirect('/')

@app.route('/payment_fail')
def payment_fail():
    return '''
    <h3>Payment Failed!</h3>
    <a href="/payment">Try Again</a> | <a href="/">Cancel and Return Home</a>
    '''

def send_order_email(to_email, order_id, cart, customer):
    from email.message import EmailMessage
    import smtplib

    msg = EmailMessage()
    msg['Subject'] = f'Order Confirmation - {order_id}'
    msg['From'] = 'crochetby3sisters@gmail.com'
    msg['To'] = to_email

    items = "\n".join([f"{item['name']} (x{item['quantity']})" for item in cart])
    body = f"""
Hello,

✅ Order ID: {order_id}
👩 Customer Name: {customer['name']}
📦 Address: {customer['address']}
📞 Phone: {customer['contact']}

🧶 Items Ordered:
{items}

Thank you for shopping with us!

- Crochet by 3 Sisters
    """

    msg.set_content(body)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login('your-email@gmail.com', 'your-app-password')
        smtp.send_message(msg)

if __name__ == "__main__":
    app.run(debug=True)
