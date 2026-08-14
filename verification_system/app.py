import os
import uuid
import psycopg2
import psycopg2.extras
import hashlib
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from ocr import process_dmart_bill

app = Flask(__name__)
app.config['SECRET_KEY'] = 'billguard-super-secret-key-123'

# --- POSTGRESQL CONFIGURATION ---
DB_USER = "postgres"
DB_PASS = "Dinesh@2006"  # Change this to your local PostgreSQL password
DB_HOST = "localhost"
DB_NAME = "billguard"

def get_db_connection():
    """Establishes a raw connection to PostgreSQL."""
    return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- FLASK-LOGIN USER CLASS ---
# Since we dropped SQLAlchemy, we must manually define the User object for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, password_hash, total_credits):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.total_credits = total_credits
        
    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    """Loads the user from PostgreSQL for session management."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM users WHERE id = %s;", (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    
    if row:
        return User(row['id'], row['username'], row['password_hash'], float(row['total_credits']))
    return None

# --- DATABASE INITIALIZATION ---
def init_db():
    """Creates the tables using raw SQL if they do not exist."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(200) NOT NULL,
            total_credits NUMERIC(10, 2) DEFAULT 0.0
        );
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS bills (
            id SERIAL PRIMARY KEY,
            bill_hash VARCHAR(64) UNIQUE NOT NULL,
            amount NUMERIC(10, 2) NOT NULL,
            credits_earned NUMERIC(10, 2) NOT NULL,
            is_duplicate BOOLEAN DEFAULT FALSE,
            scan_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
        );
    ''')
    
    # NEW: Table for the POS software integration
    cur.execute('''
        CREATE TABLE IF NOT EXISTS issued_bills (
            id SERIAL PRIMARY KEY,
            bill_hash VARCHAR(64) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    
    # Seed admin user if it doesn't exist
    cur.execute("SELECT id FROM users WHERE username = 'admin';")
    if not cur.fetchone():
        hashed_pw = generate_password_hash("admin123", method="scrypt")
        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s);", 
            ("admin", hashed_pw)
        )
        
    conn.commit()
    cur.close()
    conn.close()

with app.app_context():
    init_db()

# --- AUTH ROUTES ---
@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        if current_user.username == "admin":
            return redirect(url_for("admin_dashboard"))
        return redirect(url_for("index"))
        
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT id FROM users WHERE username = %s;", (username,))
        if cur.fetchone():
            flash("Username already exists.", "error")
            cur.close()
            conn.close()
            return redirect(url_for("register"))
            
        hashed_pw = generate_password_hash(password, method='scrypt')
        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s);", 
            (username, hashed_pw)
        )
        conn.commit()
        cur.close()
        conn.close()
        
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("login"))
        
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if current_user.username == "admin":
            return redirect(url_for("admin_dashboard"))
        return redirect(url_for("index"))
        
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM users WHERE username = %s;", (username,))
        user_row = cur.fetchone()
        cur.close()
        conn.close()
        
        if user_row and check_password_hash(user_row['password_hash'], password):
            user_obj = User(user_row['id'], user_row['username'], user_row['password_hash'], float(user_row['total_credits']))
            login_user(user_obj)
            if user_obj.username == "admin":
                return redirect(url_for("admin_dashboard"))
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password.", "error")
            
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# --- APP ROUTES ---
@app.route("/")
@login_required
def index():
    if current_user.username == "admin":
        return redirect(url_for("admin_dashboard"))
    return render_template("index.html")

@app.route("/scan", methods=["POST"])
@login_required
def scan():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    ext = os.path.splitext(file.filename)[1]
    temp_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}{ext}")
    file.save(temp_path)

    try:
        result = process_dmart_bill(temp_path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    if result["status"] == "accepted" and result["hash"]:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            cur.execute("SELECT id FROM issued_bills WHERE bill_hash = %s;", (result["hash"],))
            if not cur.fetchone():
                result["status"] = "rejected"
                result["message"] = "Fraud Alert: This bill was never issued by the POS system."
                return jsonify(result)
            
            cur.execute("SELECT user_id FROM bills WHERE bill_hash = %s AND is_duplicate = FALSE;", (result["hash"],))
            ramu = cur.fetchone()
            
            if ramu:
                result["is_duplicate"] = True
                result["message"] = "The bill already exists."
                result["credits_earned"] = 0.0
                
                somu = f"fake_{uuid.uuid4().hex}"
                
                cur.execute(
                    "INSERT INTO bills (bill_hash, amount, credits_earned, is_duplicate, user_id) VALUES (%s, %s, %s, %s, %s);",
                    (somu, float(result["amount"]), 0.0, True, current_user.id)
                )
                
            else:
                result["is_duplicate"] = False
                result["message"] = "Original bill verified."
                
                ladka = float(result["amount"])
                paisa = round(ladka * 0.1, 2)
                result["credits_earned"] = paisa
                
                current_user.total_credits += paisa
                cur.execute("UPDATE users SET total_credits = total_credits + %s WHERE id = %s;", (paisa, current_user.id))
                
                cur.execute(
                    "INSERT INTO bills (bill_hash, amount, credits_earned, is_duplicate, user_id) VALUES (%s, %s, %s, %s, %s);",
                    (result["hash"], ladka, paisa, False, current_user.id)
                )
                
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"\n[FATAL DB ERROR]: {str(e)}\n") 
            return jsonify({"error": str(e)}), 500
        finally:
            cur.close()
            conn.close()

    return jsonify(result)

@app.route("/history", methods=["GET"])
@login_required
def history():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cur.execute("SELECT bill_hash, amount, credits_earned FROM bills WHERE user_id = %s ORDER BY id DESC;", (current_user.id,))
    user_bills = cur.fetchall()
    
    cur.close()
    conn.close()
    
    records = []
    for b in user_bills:
        records.append({
            "hash": b['bill_hash'],
            "amount": f"{b['amount']:.2f}",
            "credits_earned": f"{b['credits_earned']:.2f}"
        })
        
    return jsonify({
        "username": current_user.username,
        "total_credits": round(current_user.total_credits, 2),
        "history": records
    })

# --- ADMIN ROUTES ---
@app.route("/admin")
@login_required
def admin_dashboard():
    if current_user.username != "admin":
        flash("You do not have permission to access that page.", "error")
        return redirect(url_for("index"))
        
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cur.execute("SELECT * FROM users;")
    users = cur.fetchall()
    
    bill_filter = request.args.get("filter", "all")
    if bill_filter == "original":
        cur.execute("SELECT * FROM bills WHERE is_duplicate = FALSE ORDER BY scan_date DESC;")
    elif bill_filter == "fake":
        cur.execute("SELECT * FROM bills WHERE is_duplicate = TRUE ORDER BY scan_date DESC;")
    else:
        cur.execute("SELECT * FROM bills ORDER BY scan_date DESC;")
    bills = cur.fetchall()
    
    cur.execute("SELECT COUNT(*) FROM bills WHERE is_duplicate = TRUE;")
    fake_bills_count = cur.fetchone()[0]
    
    cur.close()
    conn.close()
    
    return render_template("admin.html", users=users, bills=bills, fake_bills=fake_bills_count, current_filter=bill_filter)

@app.route("/admin/edit_credit/<int:user_id>", methods=["POST"])
@login_required
def edit_credit(user_id):
    if current_user.username != "admin":
        return jsonify({"error": "Unauthorized"}), 403
        
    new_credit = request.form.get("credits", type=float)
    if new_credit is not None:
        conn = get_db_connection()
        cur = conn.cursor()
        # Prevent editing admin
        cur.execute("SELECT username FROM users WHERE id = %s;", (user_id,))
        target_user = cur.fetchone()
        
        if target_user and target_user[0] != "admin":
            cur.execute("UPDATE users SET total_credits = %s WHERE id = %s;", (new_credit, user_id))
            conn.commit()
            
        cur.close()
        conn.close()
        
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/delete_user/<int:user_id>", methods=["POST"])
@login_required
def delete_user(user_id):
    if current_user.username != "admin":
        return jsonify({"error": "Unauthorized"}), 403
        
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT username FROM users WHERE id = %s;", (user_id,))
    target_user = cur.fetchone()
    
    if target_user and target_user[0] != "admin":
        # Bills cascade delete automatically due to ON DELETE CASCADE in table setup
        cur.execute("DELETE FROM users WHERE id = %s;", (user_id,))
        conn.commit()
        
    cur.close()
    conn.close()
    
    return redirect(url_for("admin_dashboard"))

# --- POS INTEGRATION API ---
@app.route('/api/pos/issue-bill', methods=['POST'])
def pos_webhook():
    """
    Webhook to receive completed transaction data from ABC Supermarket POS.
    Generates a secure hash and stores it in the IssuedBill ledger.
    """
    data = request.get_json()
    bill_number = data.get('bill_number')
    date_str = data.get('date')

    if not bill_number or not date_str:
        return jsonify({"error": "Missing bill_number or date"}), 400

    unique_string = f"{bill_number}_{date_str}"
    bill_hash = hashlib.sha256(unique_string.encode()).hexdigest()

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO issued_bills (bill_hash) VALUES (%s) ON CONFLICT (bill_hash) DO NOTHING;",
            (bill_hash,)
        )
        conn.commit()
        return jsonify({"status": "success", "message": "Bill registered in ledger."}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    app.run(debug=True, port=5000)