import sqlite3
from config import DEFAULT_SETTINGS

DB_PATH = "ecommerce_bot.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        falling_stars INTEGER DEFAULT 0,
        stellar_stars INTEGER DEFAULT 0,
        is_blocked INTEGER DEFAULT 0,
        joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Products table
    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        icon TEXT,
        price INTEGER NOT NULL,
        validity_days INTEGER NOT NULL,
        star_earn INTEGER NOT NULL,
        description TEXT,
        is_active INTEGER DEFAULT 1,
        rating REAL DEFAULT 0,
        review_count INTEGER DEFAULT 0
    )''')
    
    # Orders table
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        email TEXT,
        password TEXT,
        payment_proof TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        approved_at TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(user_id),
        FOREIGN KEY(product_id) REFERENCES products(id)
    )''')
    
    # Reviews table
    c.execute('''CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
        comment TEXT,
        is_approved INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(user_id),
        FOREIGN KEY(product_id) REFERENCES products(id)
    )''')
    
    # Export requests table
    c.execute('''CREATE TABLE IF NOT EXISTS export_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        post_link TEXT,
        stars_amount INTEGER NOT NULL,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        approved_at TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )''')
    
    # Settings table
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )''')
    
    # Insert default settings if not exist
    for key, val in DEFAULT_SETTINGS.items():
        c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, val))
    
    # Insert sample products if none
    c.execute("SELECT COUNT(*) FROM products")
    if c.fetchone()[0] == 0:
        sample_products = [
            ("Netflix", "🎬", 120, 7, 1, "Enjoy full access to Netflix Premium content for 7 days. Use a temporary/non-personal email for login.", 1),
            ("Spotify", "🎵", 100, 30, 1, "Spotify Premium account for 30 days. Use temporary email.", 1),
            ("VPN", "🔐", 150, 30, 1, "High-speed VPN with multiple locations. 30 days validity.", 1),
            ("Disney+ Hotstar", "🎬", 130, 7, 1, "Disney+ Hotstar Premium 7 days.", 1),
            ("YouTube", "📹", 80, 7, 1, "YouTube Premium 7 days.", 1),
            ("Amazon Prime", "🎬", 140, 7, 1, "Amazon Prime Video 7 days.", 1),
            ("Hulu", "🎬", 120, 7, 1, "Hulu Premium 7 days.", 1),
            ("Office 365", "💻", 200, 30, 2, "Microsoft Office 365 account 30 days.", 1)
        ]
        for prod in sample_products:
            c.execute('''INSERT INTO products (name, icon, price, validity_days, star_earn, description, is_active)
                         VALUES (?, ?, ?, ?, ?, ?, ?)''', prod)
    
    conn.commit()
    conn.close()

def get_db():
    return sqlite3.connect(DB_PATH)

def get_setting(key):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def set_setting(key, value):
    conn = get_db()
    c = conn.cursor()
    c.execute("REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def register_user(user_id, username, first_name):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)", 
              (user_id, username, first_name))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def update_user_stars(user_id, falling_delta=0, stellar_delta=0):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE users SET falling_stars = falling_stars + ?, stellar_stars = stellar_stars + ? WHERE user_id = ?",
              (falling_delta, stellar_delta, user_id))
    conn.commit()
    conn.close()

def add_order(user_id, product_id, email, password, payment_proof=None):
    conn = get_db()
    c = conn.cursor()
    c.execute('''INSERT INTO orders (user_id, product_id, email, password, payment_proof, status)
                 VALUES (?, ?, ?, ?, ?, 'pending')''', (user_id, product_id, email, password, payment_proof))
    order_id = c.lastrowid
    conn.commit()
    conn.close()
    return order_id

def get_product(product_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    prod = c.fetchone()
    conn.close()
    return prod

def get_all_products(active_only=True):
    conn = get_db()
    c = conn.cursor()
    if active_only:
        c.execute("SELECT * FROM products WHERE is_active = 1")
    else:
        c.execute("SELECT * FROM products")
    prods = c.fetchall()
    conn.close()
    return prods

def update_product(product_id, **kwargs):
    conn = get_db()
    c = conn.cursor()
    fields = []
    values = []
    for k, v in kwargs.items():
        fields.append(f"{k} = ?")
        values.append(v)
    values.append(product_id)
    c.execute(f"UPDATE products SET {', '.join(fields)} WHERE id = ?", values)
    conn.commit()
    conn.close()

def delete_product(product_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()

def add_review(user_id, product_id, rating, comment):
    conn = get_db()
    c = conn.cursor()
    c.execute('''INSERT INTO reviews (user_id, product_id, rating, comment, is_approved) 
                 VALUES (?, ?, ?, ?, ?)''', (user_id, product_id, rating, comment, 0))
    conn.commit()
    conn.close()

def get_pending_reviews():
    conn = get_db()
    c = conn.cursor()
    c.execute('''SELECT r.id, r.user_id, r.product_id, r.rating, r.comment, p.name 
                 FROM reviews r JOIN products p ON r.product_id = p.id 
                 WHERE r.is_approved = 0''')
    rows = c.fetchall()
    conn.close()
    return rows

def approve_review(review_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE reviews SET is_approved = 1 WHERE id = ?", (review_id,))
    # Update product rating
    c.execute('''SELECT AVG(rating), COUNT(*) FROM reviews WHERE product_id = 
                 (SELECT product_id FROM reviews WHERE id = ?) AND is_approved = 1''', (review_id,))
    avg, cnt = c.fetchone()
    if avg:
        prod_id = c.execute("SELECT product_id FROM reviews WHERE id = ?", (review_id,)).fetchone()[0]
        c.execute("UPDATE products SET rating = ?, review_count = ? WHERE id = ?", (round(avg,1), cnt, prod_id))
    conn.commit()
    conn.close()

def reject_review(review_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM reviews WHERE id = ?", (review_id,))
    conn.commit()
    conn.close()

def add_export_request(user_id, post_link, stars_amount):
    conn = get_db()
    c = conn.cursor()
    c.execute('''INSERT INTO export_requests (user_id, post_link, stars_amount, status) 
                 VALUES (?, ?, ?, 'pending')''', (user_id, post_link, stars_amount))
    req_id = c.lastrowid
    conn.commit()
    conn.close()
    return req_id

def get_pending_exports():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT e.id, e.user_id, e.post_link, e.stars_amount, u.username 
        FROM export_requests e 
        JOIN users u ON e.user_id = u.user_id 
        WHERE e.status = 'pending'
    """)
    rows = c.fetchall()
    conn.close()
    return rows

def approve_export(req_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE export_requests SET status = 'approved', approved_at = CURRENT_TIMESTAMP WHERE id = ?", (req_id,))
    # Deduct stellar stars from user
    c.execute("SELECT user_id, stars_amount FROM export_requests WHERE id = ?", (req_id,))
    user_id, stars = c.fetchone()
    c.execute("UPDATE users SET stellar_stars = stellar_stars - ? WHERE user_id = ?", (stars, user_id))
    conn.commit()
    conn.close()

def reject_export(req_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE export_requests SET status = 'rejected' WHERE id = ?", (req_id,))
    conn.commit()
    conn.close()

def get_pending_orders():
    conn = get_db()
    c = conn.cursor()
    c.execute('''SELECT o.id, o.user_id, o.product_id, o.email, o.password, o.payment_proof, p.name, u.username
                 FROM orders o JOIN products p ON o.product_id = p.id JOIN users u ON o.user_id = u.user_id
                 WHERE o.status = 'pending' ''')
    rows = c.fetchall()
    conn.close()
    return rows

def approve_order(order_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE orders SET status = 'approved', approved_at = CURRENT_TIMESTAMP WHERE id = ?", (order_id,))
    # Add stars to user
    c.execute("SELECT user_id, product_id FROM orders WHERE id = ?", (order_id,))
    user_id, prod_id = c.fetchone()
    c.execute("SELECT star_earn FROM products WHERE id = ?", (prod_id,))
    star_earn = c.fetchone()[0]
    c.execute("UPDATE users SET falling_stars = falling_stars + ? WHERE user_id = ?", (star_earn, user_id))
    conn.commit()
    conn.close()
    return user_id, star_earn

def reject_order(order_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE orders SET status = 'rejected' WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()

def get_total_revenue():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT SUM(p.price) FROM orders o JOIN products p ON o.product_id = p.id WHERE o.status = 'approved'")
    rev = c.fetchone()[0]
    conn.close()
    return rev or 0

def get_all_users():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT user_id, username, falling_stars, stellar_stars, is_blocked FROM users")
    users = c.fetchall()
    conn.close()
    return users

def block_user(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE users SET is_blocked = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def unblock_user(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE users SET is_blocked = 0 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def adjust_user_stars(user_id, falling, stellar):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE users SET falling_stars = ?, stellar_stars = ? WHERE user_id = ?", (falling, stellar, user_id))
    conn.commit()
    conn.close()

def convert_falling_to_stellar(user_id, amount):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT falling_stars FROM users WHERE user_id = ?", (user_id,))
    falling = c.fetchone()[0]
    rate = int(get_setting("falling_to_stellar"))
    if falling >= amount * rate:
        new_falling = falling - (amount * rate)
        new_stellar = amount
        c.execute("UPDATE users SET falling_stars = ?, stellar_stars = stellar_stars + ? WHERE user_id = ?", 
                  (new_falling, new_stellar, user_id))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False
