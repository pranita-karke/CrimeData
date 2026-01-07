from flask import Flask, jsonify, request, render_template, send_file
import sqlite3
import pandas as pd
import os

app = Flask(__name__)
DB_FILE = 'crime_data.db'

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/dashboard/stats')
def get_dashboard_stats():
    conn = get_db_connection()
    try:
        # Total cases
        total_cases = conn.execute('SELECT SUM(total_cases) FROM main_crime').fetchone()[0] or 0
        
        # Total Opened/Closed (Police)
        police_stats = conn.execute('SELECT SUM(opened_cases), SUM(closed_cases) FROM police_performance').fetchone()
        opened = police_stats[0] or 0
        closed = police_stats[1] or 0
        clearance_rate = (closed / opened * 100) if opened > 0 else 0
        
        # Top Crime Type
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
    # Return all for client-side filtering or implement filtering here
    # For now returning all rows limited or specific stats?
    # Requirement: Victim gender distribution, education, etc.
    # It's better to return the full dataset for this sheet if it's small (35 rows?)
    # Wait, check row count for demographics. Inspect showed ~35 rows?
    # If 35 rows, returning all is fine.
    
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
        "MAKWANPUR": "Makawanpur", 
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

    conn = get_db_connection()
    # Search with LIKE for flexibility (e.g. "Rukum" -> "Rukum West")
    query = "SELECT station_name, phone FROM police_stations WHERE district LIKE ? COLLATE NOCASE"
    rows = conn.execute(query, (f"{district}%",)).fetchall()
    conn.close()
    
    return jsonify([{'name': r[0], 'phone': r[1]} for r in rows])

if __name__ == '__main__':
    app.run(debug=True, port=5001)
