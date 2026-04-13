from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret"

# ---------- DB ----------
def db():
    con = sqlite3.connect("food.db")
    con.row_factory = sqlite3.Row
    return con

# ---------- CREATE TABLES ----------
def create_tables():
    con = db()

    con.execute('''
    CREATE TABLE IF NOT EXISTS donors(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        address TEXT,
        email TEXT,
        password TEXT
    )
    ''')

    con.execute('''
    CREATE TABLE IF NOT EXISTS ngos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        owner TEXT,
        address TEXT,
        phone TEXT,
        email TEXT,
        type TEXT,
        password TEXT
    )
    ''')

    con.execute('''
    CREATE TABLE IF NOT EXISTS donations(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        donor_id INTEGER,
        food_name TEXT,
        quantity TEXT,
        phone TEXT,
        prepared TEXT,
        expiry TEXT,
        location TEXT,
        status TEXT,
        ngo_id INTEGER,
        delivery_partner_id INTEGER
    )
    ''')

    # Add schema fixes for older databases
    existing_columns = [row['name'] for row in con.execute("PRAGMA table_info(donations)").fetchall()]
    if 'delivery_partner_id' not in existing_columns:
        con.execute("ALTER TABLE donations ADD COLUMN delivery_partner_id INTEGER")

    con.execute('''
    CREATE TABLE IF NOT EXISTS delivery_partners(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        email TEXT,
        address TEXT,
        vehicle_type TEXT,
        vehicle_number TEXT,
        company TEXT,
        password TEXT
    )
    ''')

    # Add missing delivery partner address column to older databases
    partner_columns = [row['name'] for row in con.execute("PRAGMA table_info(delivery_partners)").fetchall()]
    if 'address' not in partner_columns:
        con.execute("ALTER TABLE delivery_partners ADD COLUMN address TEXT")

    con.commit()
    con.close()

create_tables()

# ---------- HOME ----------
@app.route('/')
def home():
    return render_template('index.html')

# ---------- DONOR ----------
@app.route('/donor_register', methods=['GET','POST'])
def donor_register():
    if request.method == 'POST':
        con = db()
        con.execute('''
        INSERT INTO donors(name, phone, address, email, password)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            request.form['name'],
            request.form['phone'],
            request.form['address'],
            request.form['email'],
            request.form['password']
        ))
        con.commit()
        con.close()
        return redirect('/donor_login')
    return render_template('donor_register.html')


@app.route('/donor_login', methods=['GET','POST'])
def donor_login():
    if request.method == 'POST':
        con = db()
        user = con.execute(
            "SELECT * FROM donors WHERE email=? AND password=?",
            (request.form['email'], request.form['password'])
        ).fetchone()
        con.close()

        if user:
            session['donor'] = user['id']
            return redirect('/donor_dashboard')
        else:
            return render_template('donor_login.html', error="Invalid login id")
    return render_template('donor_login.html')

@app.route('/donor_dashboard', methods=['GET', 'POST'])
def donor_dashboard():
    if 'donor' not in session:
        return redirect('/donor_login')

    con = db()

    if request.method == 'POST':
        food_name = request.form.get('food_name')
        quantity = request.form.get('quantity')
        prepared = request.form.get('prepared')
        
        location = request.form.get('location')
        phone = request.form.get('phone')
        
        con.execute("""
        INSERT INTO donations
        (donor_id, food_name, quantity, phone, prepared, location, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            session['donor'],
            food_name,
            quantity,
            phone,
            prepared,
            location,
            "Available"
        ))

        con.commit()

    foods = con.execute("""
        SELECT * FROM donations
        WHERE donor_id=?
        ORDER BY id DESC
    """, (session['donor'],)).fetchall()

    con.close()

    return render_template('donor_dashboard.html', foods=foods)




# ---------- NGO ----------
@app.route('/ngo_register', methods=['GET','POST'])
def ngo_register():
    if request.method == 'POST':
        con = db()
        con.execute('''
        INSERT INTO ngos(name, owner, address, phone, email, type, password)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            request.form['name'],
            request.form['owner'],
            request.form['address'],
            request.form['phone'],
            request.form['email'],
            request.form['type'],
            request.form['password']
        ))
        con.commit()
        con.close()
        return redirect('/ngo_login')
    return render_template('ngo_register.html')


@app.route('/ngo_login', methods=['GET','POST'])
def ngo_login():
    if request.method == 'POST':
        con = db()
        user = con.execute(
            "SELECT * FROM ngos WHERE email=? AND password=?",
            (request.form['email'], request.form['password'])
        ).fetchone()
        con.close()

        if user:
            session['ngo'] = user['id']
            return redirect('/ngo_dashboard')
        else:
            return render_template('ngo_login.html', error="Invalid login id")
    return render_template('ngo_login.html')


@app.route('/ngo_dashboard')
def ngo_dashboard():
    if 'ngo' not in session:
        return redirect('/ngo_login')

    con = db()

    foods = con.execute('''
    SELECT donations.*, donors.name, donors.phone, ngos.name as ngo_name
    FROM donations
    JOIN donors ON donors.id = donations.donor_id
    LEFT JOIN ngos ON ngos.id = donations.ngo_id
    ''').fetchall()

    con.close()

    current_ngo = session['ngo']
    has_available = any(food['status'] == 'Available' for food in foods)
    has_accepted = any(food['status'] == 'Donated' and food['ngo_id'] == current_ngo for food in foods)

    return render_template('ngo_dashboard.html', foods=foods, has_available=has_available, has_accepted=has_accepted, current_ngo=current_ngo)


@app.route('/accept/<int:id>')
def accept(id):
    if 'ngo' not in session:
        return redirect('/ngo_login')

    con = db()
    donation = con.execute("SELECT * FROM donations WHERE id=?", (id,)).fetchone()
    con.close()

    return render_template('accept_donation.html', donation=donation)

@app.route('/confirm_accept/<int:id>/<method>', methods=['POST'])
@app.route('/confirm_accept/<int:id>/<method>/<int:partner_id>', methods=['POST'])
def confirm_accept(id, method, partner_id=None):
    if 'ngo' not in session:
        return redirect('/ngo_login')

    con = db()
    if partner_id:
        con.execute(
            "UPDATE donations SET status='Donated', ngo_id=?, delivery_partner_id=? WHERE id=?",
            (session['ngo'], partner_id, id)
        )
    else:
        con.execute(
            "UPDATE donations SET status='Donated', ngo_id=? WHERE id=?",
            (session['ngo'], id)
        )
    con.commit()
    con.close()

    return redirect('/ngo_dashboard?accepted=true')

@app.route('/get_delivery_partners')
def get_delivery_partners():
    con = db()
    partners = con.execute("SELECT * FROM delivery_partners").fetchall()
    con.close()
    return [{'id': p['id'], 'name': p['name'], 'phone': p['phone'], 'vehicle_type': p['vehicle_type'], 'vehicle_number': p['vehicle_number'], 'company': p['company']} for p in partners]

@app.route('/get_all_locations')
def get_all_locations():
    con = db()
    ngos = con.execute("SELECT name, address FROM ngos").fetchall()
    donors = con.execute("SELECT name, address FROM donors").fetchall()
    partners = con.execute("SELECT name, address, vehicle_type FROM delivery_partners").fetchall()
    con.close()
    
    return {
        'ngos': [{'name': n['name'], 'address': n['address']} for n in ngos],
        'donors': [{'name': d['name'], 'address': d['address']} for d in donors],
        'partners': [{'name': p['name'], 'address': p['address'], 'vehicle_type': p['vehicle_type']} for p in partners]
    }

# ---------- SEARCH (MAIN FEATURE) ----------
@app.route('/search', methods=['GET','POST'])
def search():
    con = db()

    ngos = []
    foods = []

    if request.method == 'POST':
        location = request.form.get('location')
        food_type = request.form.get('food_type')

        # NGOs by location
        if location:
            ngos = con.execute(
                "SELECT * FROM ngos WHERE address LIKE ?",
                ('%' + location + '%',)
            ).fetchall()

        # Food search
        query = '''
        SELECT donations.*, donors.name, donors.phone, ngos.name as ngo_name
        FROM donations
        JOIN donors ON donors.id = donations.donor_id
        LEFT JOIN ngos ON ngos.id = donations.ngo_id
        WHERE 1=1
        '''
        params = []

        if food_type:
            query += " AND donations.food_name LIKE ?"
            params.append('%' + food_type + '%')

        if location:
            query += " AND donations.location LIKE ?"
            params.append('%' + location + '%')

        foods = con.execute(query, params).fetchall()

    con.close()

    return render_template('search.html', ngos=ngos, foods=foods)

# ---------- ADMIN ----------
@app.route('/admin_login', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['user'] == "admin" and request.form['pass'] == "admin123":
            session['admin'] = True
            return redirect('/admin_dashboard')
        else:
            return render_template('admin_login.html', error="Invalid credentials")
    return render_template('admin_login.html')


@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect('/admin_login')

    con = db()

    donors = con.execute("SELECT COUNT(*) FROM donors").fetchone()[0]
    ngos = con.execute("SELECT COUNT(*) FROM ngos").fetchone()[0]
    donations = con.execute("SELECT COUNT(*) FROM donations").fetchone()[0]

    all_donors = con.execute("SELECT * FROM donors").fetchall()
    all_ngos = con.execute("SELECT * FROM ngos").fetchall()

    con.close()

    return render_template('admin_dashboard.html',
                           donors=donors,
                           ngos=ngos,
                           donations=donations,
                           all_donors=all_donors,
                           all_ngos=all_ngos)

# ---------- DELETE ----------
@app.route('/delete_donor/<int:id>')
def delete_donor(id):
    con = db()
    con.execute("DELETE FROM donors WHERE id=?", (id,))
    con.commit()
    con.close()
    return redirect('/admin_dashboard')


@app.route('/delete_ngo/<int:id>')
def delete_ngo(id):
    con = db()
    con.execute("DELETE FROM ngos WHERE id=?", (id,))
    con.commit()
    con.close()
    return redirect('/admin_dashboard')

# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ---------- DELIVERY PARTNERS ----------
@app.route('/delivery_partners')
def delivery_partners():
    con = db()
    partners = con.execute("SELECT * FROM delivery_partners").fetchall()
    con.close()
    return render_template('delivery_partners.html', partners=partners)

@app.route('/delivery_register', methods=['GET','POST'])
def delivery_register():
    if request.method == 'POST':
        con = db()
        con.execute('''
        INSERT INTO delivery_partners(name, phone, email, address, vehicle_type, vehicle_number, company, password)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            request.form['name'],
            request.form['phone'],
            request.form['email'],
            request.form['address'],
            request.form['vehicle_type'],
            request.form['vehicle_number'],
            request.form['company'],
            request.form['password']
        ))
        con.commit()
        con.close()
        return redirect('/delivery_partners')
    return render_template('delivery_register.html')

@app.route('/view_donations')
def view_donations():
    con = db()
    foods = con.execute('''
    SELECT donations.*, donors.name, donors.phone, ngos.name as ngo_name, 
           delivery_partners.name as partner_name, delivery_partners.phone as partner_phone,
           delivery_partners.vehicle_type, delivery_partners.vehicle_number
    FROM donations
    JOIN donors ON donors.id = donations.donor_id
    LEFT JOIN ngos ON ngos.id = donations.ngo_id
    LEFT JOIN delivery_partners ON delivery_partners.id = donations.delivery_partner_id
    ORDER BY donations.id DESC
    ''').fetchall()
    con.close()
    return render_template('view_donations.html', foods=foods)

@app.route('/map')
def map_page():
    return render_template('map_page.html')

@app.route('/api/map_locations')
def map_locations():
    con = db()
    
    # Get all donors with their locations
    donors = con.execute("SELECT id, name, address, phone FROM donors").fetchall()
    
    # Get all NGOs with their locations
    ngos = con.execute("SELECT id, name, address, phone FROM ngos").fetchall()
    
    # Get all delivery partners
    partners = con.execute("SELECT id, name, vehicle_type FROM delivery_partners").fetchall()
    
    # Get all donations with locations
    donations = con.execute("""
    SELECT donations.id, donations.food_name, donations.location, donations.status, 
           donations.quantity, donors.name as donor_name, ngos.name as ngo_name
    FROM donations
    JOIN donors ON donors.id = donations.donor_id
    LEFT JOIN ngos ON ngos.id = donations.ngo_id
    """).fetchall()
    
    con.close()
    
    return {
        'donors': [{'id': d['id'], 'name': d['name'], 'address': d['address'], 'phone': d['phone']} for d in donors],
        'ngos': [{'id': n['id'], 'name': n['name'], 'address': n['address'], 'phone': n['phone']} for n in ngos],
        'partners': [{'id': p['id'], 'name': p['name'], 'vehicle_type': p['vehicle_type']} for p in partners],
        'donations': [{'id': d['id'], 'food_name': d['food_name'], 'location': d['location'], 'status': d['status'], 'quantity': d['quantity'], 'donor_name': d['donor_name'], 'ngo_name': d['ngo_name']} for d in donations]
    }

# ---------- RUN ----------
if __name__ == '__main__':
    app.run(debug=True)