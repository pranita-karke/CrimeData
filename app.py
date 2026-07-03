from flask import Flask, jsonify, request, render_template, send_file, session, redirect, url_for
import sqlite3
import pandas as pd
import os
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_demo' # Change in production
DB_FILE = 'crime_data.db'

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_tables():
    conn = get_db_connection()
    # FIR Table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS firs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            province TEXT,
            district TEXT,
            police_station TEXT,
            contact_info TEXT,
            crime_type TEXT,
            description TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Users Table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL, -- 'user', 'police', 'admin'
            police_station TEXT, -- Nullable, only for police
            district TEXT, -- Nullable, only for police
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Alerts Table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            district TEXT NOT NULL,
            message TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            accepted_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            sender_name TEXT
        )
    ''')
    
    # Fixed Admin User
    admin = conn.execute('SELECT * FROM users WHERE role = ?', ('admin',)).fetchone()
    if not admin:
        hashed_pw = generate_password_hash('admin123')
        conn.execute('''
            INSERT INTO users (full_name, username, password_hash, role)
            VALUES (?, ?, ?, ?)
        ''', ('System Administrator', 'admin', hashed_pw, 'admin'))
        
    conn.commit()
    conn.close()

# Initialize tables on start
try:
    init_tables()
except Exception as e:
    print(f"Error initializing tables: {e}")

@app.route('/')
def index():
    if 'user_id' in session:
        return render_template('index.html', user=session)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['full_name'] = user['full_name']
            if user['role'] == 'police':
                session['station'] = user['police_station']
                session['district'] = user['district']
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid username or password")
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        if role == 'admin':
            return render_template('register.html', error="Admin registration is not allowed.")
        
        # Police specific fields
        police_station = request.form.get('police_station')
        district = request.form.get('district')
        
        if not username or not password or not full_name:
             return render_template('register.html', error="All fields are required")

        hashed_pw = generate_password_hash(password)
        
        # --- Handle New Station ---
        if role == 'police' and police_station == 'Other':
            new_station = request.form.get('new_station_name')
            new_phone = request.form.get('new_station_phone')
            
            if not new_station:
                 return render_template('register.html', error="New Station Name is required")
            
            new_station = new_station.strip().title()
            
            try:
                conn = get_db_connection()
                # Insert if not exists (or fail/ignore)
                conn.execute('INSERT INTO police_stations (station_name, district, phone) VALUES (?, ?, ?)',
                             (new_station, district, new_phone))
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"Error adding station: {e}")
            
            police_station = new_station

        try:
            conn = get_db_connection()
            conn.execute('''
                INSERT INTO users (full_name, username, password_hash, role, police_station, district)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (full_name, username, hashed_pw, role, police_station, district))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return render_template('register.html', error="Username already exists")
        except Exception as e:
            return render_template('register.html', error=str(e))
            
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/my_complaints')
def my_complaints():
    if 'user_id' not in session or session.get('role') != 'police':
        return jsonify({'error': 'Unauthorized'}), 403
        
    try:
        station_name = session.get('station')
        if not station_name:
            print("DEBUG MATCH: Error - Station Name is None", flush=True)
            return jsonify([])

        conn = get_db_connection()
        all_firs = conn.execute("SELECT * FROM firs ORDER BY created_at DESC").fetchall()
        conn.close()
        
        
        import difflib
        
        matches = []
        
        def normalize(s):
            if not s: return ""
            # Remove all spaces and non-alphanumeric, plain lowercase
            return ''.join(c for c in s.lower() if c.isalnum())

        def get_core_name(s):
            if not s: return ""
            s = s.lower()
            # Remove common prefixes/suffixes to compare only the location Name
            ignore_words = ["district", "police", "office", "dpo", "metropolitan", "submetropolitan", "municipality", "rural", "station", "area", "apo", "range", "ward", "woda", "post", "chowki", "circle", "sector", "beat"]
            for w in ignore_words:
                s = s.replace(w, "")
            # Return normalized core
            return ''.join(c for c in s if c.isalnum())
            
        norm_session = normalize(station_name)
        core_session = get_core_name(station_name)
        
        print(f"DEBUG MATCH: Session='{station_name}', Norm='{norm_session}', Core='{core_session}'", flush=True)

        for row in all_firs:
            f_station = row['police_station']
            if not f_station: continue
            
            norm_fir = normalize(f_station)
            core_fir = get_core_name(f_station)
            
            # 1. Exact containment of FULL strings (if user provided very specific name)
            if norm_session in norm_fir or norm_fir in norm_session:
                matches.append(dict(row))
                continue
                
            # 2. Fuzzy Similarity on CORE name only (Avoids "District Police Office" causing 80% match)
            # Only check if we have a core name (avoid matching empty strings)
            if len(core_session) > 2 and len(core_fir) > 2:
                ratio = difflib.SequenceMatcher(None, core_session, core_fir).ratio()
                if ratio > 0.85: # Increased threshold strictly for core names
                    print(f"DEBUG MATCH: Fuzzy Core Match {ratio:.2f} for '{f_station}'", flush=True)
                    matches.append(dict(row))

        print(f"DEBUG MATCH: Found {len(matches)} complaints", flush=True)
        return jsonify(matches)
        
    except Exception as e:
        print(f"ERROR in my_complaints: {e}", flush=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/my_alerts')
def my_alerts():
    if 'user_id' not in session or session.get('role') != 'police':
        return jsonify({'error': 'Unauthorized'}), 403
    
    district = session.get('district')
    # Fetch alerts for this district (last 24 hours/active)
    print(f"DEBUG ALERTS: Fetching for district '{district}'", flush=True)
    conn = get_db_connection()
    try:
        alerts = conn.execute('''
            SELECT id, district, message, status, accepted_by, created_at, sender_name FROM alerts 
            WHERE district = ? COLLATE NOCASE
            ORDER BY created_at DESC 
            LIMIT 5
        ''', (district,)).fetchall()
        print(f"DEBUG ALERTS: Found {len(alerts)} alerts", flush=True)
        return jsonify([dict(row) for row in alerts])
    finally:
        conn.close()

@app.route('/api/create_alert', methods=['POST'])
def create_alert():
    data = request.get_json()
    district = data.get('district')
    message = data.get('message', 'Emergency Reported')
    
    # Debug: Print session keys
    print(f"DEBUG SESSION: {list(session.keys())}", flush=True)
    if 'full_name' in session:
         print(f"DEBUG SESSION NAME: {session['full_name']}", flush=True)
    
    sender_name = session.get('full_name') or 'Anonymous User'
    
    print(f"DEBUG ALERTS: Creating alert for '{district}' by '{sender_name}'", flush=True)
    
    if not district:
        print("DEBUG ALERTS: Failed - No District", flush=True)
        return jsonify({'status': 'error', 'message': 'District required'}), 400
        
    conn = get_db_connection()
    try:
        cursor = conn.execute('INSERT INTO alerts (district, message, sender_name) VALUES (?, ?, ?)', (district, message, sender_name))
        conn.commit()
        return jsonify({'status': 'success', 'alert_id': cursor.lastrowid})
    finally:
        conn.close()

@app.route('/api/accept_alert', methods=['POST'])
def accept_alert():
    if 'user_id' not in session or session.get('role') != 'police':
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.get_json()
    alert_id = data.get('alert_id')
    station_name = session.get('station')
    
    conn = get_db_connection()
    try:
        # Check if already accepted
        alert = conn.execute('SELECT status FROM alerts WHERE id = ?', (alert_id,)).fetchone()
        if not alert:
            return jsonify({'status': 'error', 'message': 'Alert not found'}), 404
            
        if alert['status'] == 'Accepted':
             # Already accepted
             return jsonify({'status': 'success', 'message': 'Already accepted'})
             
        conn.execute('UPDATE alerts SET status = ?, accepted_by = ? WHERE id = ?', 
                     ('Accepted', station_name, alert_id))
        conn.commit()
        return jsonify({'status': 'success'})
    finally:
        conn.close()

@app.route('/api/alert_status/<int:alert_id>', methods=['GET'])
def get_alert_status(alert_id):
    conn = get_db_connection()
    try:
        alert = conn.execute('SELECT status, accepted_by FROM alerts WHERE id = ?', (alert_id,)).fetchone()
        if not alert:
            return jsonify({'error': 'Not found'}), 404
        return jsonify({
            'status': alert['status'],
            'accepted_by': alert['accepted_by']
        })
    finally:
        conn.close()

@app.route('/api/update_status', methods=['POST'])
def update_status():
    if 'user_id' not in session or session.get('role') != 'police':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    fir_id = data.get('id')
    status = data.get('status')
    
    conn = get_db_connection()
    try:
        conn.execute('UPDATE firs SET status = ? WHERE id = ?', (status, fir_id))
        conn.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/submit_fir', methods=['POST'])
def submit_fir():
    try:
        data = request.get_json()
        required_fields = ['full_name', 'police_station', 'description']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'status': 'error', 'message': f'Missing field: {field}'}), 400
        
        conn = get_db_connection()
        from datetime import datetime
        conn.execute('''
            INSERT INTO firs (full_name, province, district, police_station, contact_info, crime_type, description, created_at, nepali_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('full_name'),
            data.get('province'),
            data.get('district'),
            data.get('police_station'),
            data.get('contact_info'),
            data.get('crime_type'),
            data.get('description'),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            data.get('nepali_date')
        ))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'message': 'FIR submitted successfully'}), 201
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/dashboard/stats')
def get_dashboard_stats():
    conn = get_db_connection()
    try:
        
        total_cases = conn.execute('SELECT SUM(total_cases) FROM main_crime').fetchone()[0] or 0
        
        
        police_stats = conn.execute('SELECT SUM(opened_cases), SUM(closed_cases) FROM police_performance').fetchone()
        opened = police_stats[0] or 0
        closed = police_stats[1] or 0
        clearance_rate = (closed / opened * 100) if opened > 0 else 0
        
        
        top_crime = conn.execute('SELECT crime_type, SUM(total_cases) as total FROM main_crime GROUP BY crime_type ORDER BY total DESC LIMIT 1').fetchone()
        top_crime_type = top_crime['crime_type'] if top_crime else "N/A"
        
        return jsonify({
            'total_crime_cases': total_cases,
            'clearance_rate': round(clearance_rate, 2),
            'top_crime_type': top_crime_type,
            'opened_cases': opened,
            'closed_cases': closed
        })
    finally:
        conn.close()

@app.route('/api/crime/main')
def get_main_crime_data():
    year = request.args.get('year')
    province = request.args.get('province')
    district = request.args.get('district')
    crime_type = request.args.get('crime_type')
    
    print(f"DEBUG API /api/crime/main: year={year}, province={province}, district={district}", flush=True)
    
    query = "SELECT * FROM main_crime WHERE 1=1"
    params = []
    
    if year:
        query += " AND year = ?"
        params.append(year)
    if province:
        query += " AND province = ?"
        params.append(province)
    if district:
        query += " AND district = ?"
        params.append(district)
    if crime_type:
        query += " AND crime_type = ?"
        params.append(crime_type)
        
    conn = get_db_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    
    return jsonify([dict(row) for row in rows])

@app.route('/api/crime/detailed')
def get_detailed_demographics():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM victim_demographics').fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route('/api/police')
def get_police_data():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM police_performance').fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

# Filters
@app.route('/api/filters')
def get_filters():
    conn = get_db_connection()
    # Normalize values to prevent duplicates (strip whitespace, title case)
    years = [r[0].strip() for r in conn.execute('SELECT DISTINCT year FROM main_crime ORDER BY year').fetchall() if r[0]]
    provinces = sorted(list(set([r[0].strip().title() for r in conn.execute('SELECT DISTINCT province FROM main_crime').fetchall() if r[0]])))
    districts = sorted(list(set([r[0].strip().title() for r in conn.execute('SELECT DISTINCT district FROM main_crime').fetchall() if r[0]])))
    crime_types = sorted(list(set([r[0].strip() for r in conn.execute('SELECT DISTINCT crime_type FROM main_crime').fetchall() if r[0]])))
    conn.close()
    
    return jsonify({
        'years': years,
        'provinces': provinces,
        'districts': districts,
        'crime_types': crime_types
    })

@app.route('/api/export/excel')
def export_data():
    conn = get_db_connection()
    try:
        # Fetch all tables
        df_main = pd.read_sql_query("SELECT * FROM main_crime", conn)
        df_dem = pd.read_sql_query("SELECT * FROM victim_demographics", conn)
        df_pol = pd.read_sql_query("SELECT * FROM police_performance", conn)
        
        output_file = 'exported_data.xlsx'
        with pd.ExcelWriter(output_file) as writer:
            df_main.to_excel(writer, sheet_name='Crime Data', index=False)
            df_dem.to_excel(writer, sheet_name='Demographics', index=False)
            df_pol.to_excel(writer, sheet_name='Police Performance', index=False)
            
        return send_file(output_file, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/update/main', methods=['POST'])
def update_crime_record():
    # Placeholder for update logic
    return jsonify({'status': 'success', 'message': 'Update feature to be implemented'}), 200

@app.route('/api/add/main', methods=['POST'])
def add_crime_record():
    # Placeholder for add logic
    return jsonify({'status': 'success', 'message': 'Add feature to be implemented'}), 200

@app.route('/api/districts')
def get_districts():
    province = request.args.get('province')
    conn = get_db_connection()
    if province:
        # Normalize province input as well? Better to rely on DB comparison or match loosely if needed.
        # Assuming DB has mixed quality, we fetch distinct and then clean python side.
        query = "SELECT DISTINCT district FROM main_crime WHERE province = ?"
        raw_districts = [r[0] for r in conn.execute(query, (province,)).fetchall()]
    else:
        query = "SELECT DISTINCT district FROM main_crime"
        raw_districts = [r[0] for r in conn.execute(query).fetchall()]
    
    conn.close()
    
    districts = sorted(list(set([d.strip().title() for d in raw_districts if d])))
    print(f"DEBUG /api/districts: Count={len(districts)}, First 5={districts[:5]}", flush=True)
    return jsonify(districts)

@app.route('/api/crimetypes')
def get_crime_types():
    conn = get_db_connection()
    query = "SELECT DISTINCT crime_type FROM main_crime ORDER BY crime_type"
    types = [r[0] for r in conn.execute(query).fetchall()]
    conn.close()
    return jsonify(types)

import prediction

# ... (existing code) ...

@app.route('/api/predict', methods=['GET', 'POST'])
def predict_crime():
    try:
        if request.method == 'GET':
            year = request.args.get('year')
            province = request.args.get('province')
            district = request.args.get('district')
        else:
            data = request.get_json()
            year = data.get('year')
            province = data.get('province')
            district = data.get('district')
        
        # Normalize District Name (Map vs DB mismatches)
        if district:
            d_upper = district.strip().upper()
            mapping = {
                "SINDHUPALCHOWK": "Sindhupalchok",
                "CHITAWAN": "Chitwan", 
                "DHANUSA": "Dhanusha",
                "RUKHUM": "Rukum",
                "TERATHUM": "Terhathum",
                "KAPILBASTU": "Kapilvastu",
                "BARDIA": "Bardiya"
            }
            if d_upper in mapping:
                district = mapping[d_upper]
        
        print(f"DEBUG PREDICT: year={year}, province={province}, district={district}", flush=True)
        
        if not year:
            return jsonify({'error': 'Year is required'}), 400
            
        result = prediction.train_and_predict(year, province, district)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stations')
def get_stations():
    district = request.args.get('district', '').strip()
    if not district:
        return jsonify([])
    
    # Mapping for Police Data (Align with DB names if needed)
    # The import script normalized to Title Case, e.g. "Kathmandu", "Kavrepalanchok"
    # Basic mapping:
    d_upper = district.upper()
    mapping = {
        "KAVRE": "Kavrepalanchok",
        "TANAHU": "Tanahun",
        "MAKWANPUR": "Makwanpur", 
        "SINDHUPALCHOWK": "Sindhupalchok",
        "CHITAWAN": "Chitwan",
        "DHANUSA": "Dhanusha",
        "RUKHUM": "Rukum", # Or Rukum East/West? Police data assumes pre-split mostly?
        "TERATHUM": "Terhathum",
        "KAPILBASTU": "Kapilvastu",
        "BARDIA": "Bardiya"
    }
    if d_upper in mapping:
        district = mapping[d_upper]

    # Additional Logic for Valley/Metropolitan areas
    # If input is "Kathmandu Metropolitan City" -> "Kathmandu"
    # If input is "Lalitpur Metropolitan City" -> "Lalitpur"
    # If input is "Bhaktapur Municipality" -> "Bhaktapur"
    
    # Generic strip of suffixes
    suffixes = [" METROPOLITAN CITY", " SUB-METROPOLITAN CITY", " MUNICIPALITY", " RURAL MUNICIPALITY"]
    for suffix in suffixes:
        if d_upper.endswith(suffix):
            district = district[: -len(suffix)].strip().title()
            break
            
    # Specific Overrides for Valley (if they don't match standard patterns)
    if "KATHMANDU" in d_upper: 
        district = "Kathmandu"
    elif "LALITPUR" in d_upper:
        district = "Lalitpur"
    elif "BHAKTAPUR" in d_upper:
        district = "Bhaktapur"

    conn = get_db_connection()
    # Search with LIKE for flexibility (e.g. "Rukum" -> "Rukum West")
    query = "SELECT station_name, phone FROM police_stations WHERE district LIKE ? COLLATE NOCASE"
    rows = conn.execute(query, (f"{district}%",)).fetchall()
    conn.close()
    return jsonify([{'name': row['station_name'], 'phone': row['phone']} for row in rows])
    
# --- Admin Routes ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/admin/stats')
@admin_required
def admin_stats():
    conn = get_db_connection()
    user_counts = conn.execute('SELECT role, count(*) as count FROM users GROUP BY role').fetchall()
    total_firs = conn.execute('SELECT count(*) FROM firs').fetchone()[0]
    total_crime = conn.execute('SELECT count(*) FROM main_crime').fetchone()[0]
    conn.close()
    
    stats = {
        'user_stats': [dict(row) for row in user_counts],
        'total_firs': total_firs,
        'total_crime_records': total_crime
    }
    return jsonify(stats)

@app.route('/api/admin/users', methods=['GET'])
@admin_required
def admin_list_users():
    conn = get_db_connection()
    users = conn.execute('SELECT id, full_name, username, role, police_station, district, created_at FROM users').fetchall()
    conn.close()
    return jsonify([dict(row) for row in users])

@app.route('/api/admin/users/<int:user_id>', methods=['PUT', 'DELETE'])
@admin_required
def admin_manage_user(user_id):
    conn = get_db_connection()
    if request.method == 'DELETE':
        conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success'})
    
    data = request.get_json()
    full_name = data.get('full_name')
    username = data.get('username')
    role = data.get('role')
    police_station = data.get('police_station')
    district = data.get('district')
    new_password = data.get('password')

    if not full_name or not username or not role:
        return jsonify({'error': 'Required fields missing'}), 400

    try:
        if new_password:
            hashed_pw = generate_password_hash(new_password)
            conn.execute('''
                UPDATE users SET full_name = ?, username = ?, role = ?, police_station = ?, district = ?, password_hash = ?
                WHERE id = ?
            ''', (full_name, username, role, police_station, district, hashed_pw, user_id))
        else:
            conn.execute('''
                UPDATE users SET full_name = ?, username = ?, role = ?, police_station = ?, district = ?
                WHERE id = ?
            ''', (full_name, username, role, police_station, district, user_id))
        
        conn.commit()
        conn.close()
        return jsonify({'status': 'success'})
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username already exists'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/firs', methods=['GET'])
@admin_required
def admin_list_firs():
    conn = get_db_connection()
    firs = conn.execute('SELECT * FROM firs ORDER BY created_at DESC').fetchall()
    conn.close()
    return jsonify([dict(row) for row in firs])

@app.route('/api/admin/firs/<int:fir_id>', methods=['PUT', 'DELETE'])
@admin_required
def admin_manage_fir(fir_id):
    conn = get_db_connection()
    if request.method == 'DELETE':
        conn.execute('DELETE FROM firs WHERE id = ?', (fir_id,))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success'})
    
    data = request.get_json()
    conn.execute('''
        UPDATE firs SET full_name = ?, province = ?, district = ?, police_station = ?, 
        crime_type = ?, description = ?, status = ?
        WHERE id = ?
    ''', (data.get('full_name'), data.get('province'), data.get('district'), 
          data.get('police_station'), data.get('crime_type'), data.get('description'), 
          data.get('status'), fir_id))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/api/admin/crime', methods=['GET', 'POST'])
@admin_required
def admin_manage_crime_base():
    conn = get_db_connection()
    if request.method == 'GET':
        year = request.args.get('year')
        if year:
            rows = conn.execute('SELECT * FROM main_crime WHERE year = ? ORDER BY district ASC', (year,)).fetchall()
        else:
            rows = conn.execute('SELECT * FROM main_crime ORDER BY year DESC, district ASC LIMIT 1000').fetchall()
        conn.close()
        return jsonify([dict(row) for row in rows])
    
    data = request.get_json()
    conn.execute('''
        INSERT INTO main_crime (year, province, district, crime_type, total_cases)
        VALUES (?, ?, ?, ?, ?)
    ''', (data.get('year'), data.get('province'), data.get('district'), 
          data.get('crime_type'), data.get('total_cases')))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/api/admin/crime/<int:crime_id>', methods=['PUT', 'DELETE'])
@admin_required
def admin_manage_crime_item(crime_id):
    conn = get_db_connection()
    if request.method == 'DELETE':
        conn.execute('DELETE FROM main_crime WHERE id = ?', (crime_id,))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success'})
    
    data = request.get_json()
    conn.execute('''
        UPDATE main_crime SET year = ?, province = ?, district = ?, crime_type = ?, total_cases = ?
        WHERE id = ?
    ''', (data.get('year'), data.get('province'), data.get('district'), 
          data.get('crime_type'), data.get('total_cases'), crime_id))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/api/admin/stations', methods=['GET', 'POST'])
@admin_required
def admin_manage_stations_base():
    conn = get_db_connection()
    if request.method == 'GET':
        rows = conn.execute('SELECT * FROM police_stations ORDER BY district ASC, station_name ASC').fetchall()
        conn.close()
        return jsonify([dict(row) for row in rows])
    
    data = request.get_json()
    conn.execute('''
        INSERT INTO police_stations (district, station_name, phone)
        VALUES (?, ?, ?)
    ''', (data.get('district'), data.get('station_name'), data.get('phone')))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/api/admin/stations/<int:station_id>', methods=['PUT', 'DELETE'])
@admin_required
def admin_manage_station_item(station_id):
    conn = get_db_connection()
    if request.method == 'DELETE':
        conn.execute('DELETE FROM police_stations WHERE id = ?', (station_id,))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success'})
    
    data = request.get_json()
    conn.execute('''
        UPDATE police_stations SET district = ?, station_name = ?, phone = ?
        WHERE id = ?
    ''', (data.get('district'), data.get('station_name'), data.get('phone'), station_id))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True, port=5001)


