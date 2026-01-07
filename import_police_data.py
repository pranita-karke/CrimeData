import pandas as pd
import sqlite3
import os

DB_FILE = 'crime_data.db'
EXCEL_FILE = 'police_stations.xlsx'

def import_data():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create Table
    print("Creating table...")
    cursor.execute("DROP TABLE IF EXISTS police_stations")
    cursor.execute('''
        CREATE TABLE police_stations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            district TEXT,
            station_name TEXT,
            phone TEXT
        )
    ''')
    
    try:
        df = pd.read_excel(EXCEL_FILE)
        
        # Normalize columns
        df.columns = [c.strip().lower() for c in df.columns]
        print("Found columns:", df.columns.tolist())
        
        # Identify columns
        dist_col = next((c for c in df.columns if 'district' in c), None)
        phone_col = next((c for c in df.columns if 'phone' in c or 'contact' in c or 'number' in c or 'mobile' in c), None)
        name_col = next((c for c in df.columns if 'name' in c or 'unit' in c or 'station' in c or 'office' in c), None)
        
        if not (dist_col and phone_col and name_col):
            # Fallback for name if specific generic col not found (e.g. maybe it's the second col?)
            full_cols = df.columns.tolist()
            if not name_col and len(full_cols) >= 2:
                 # Assume standard: District, Name, Phone
                 name_col = full_cols[1] 
            
            if not (dist_col and phone_col and name_col):
                print(f"CRITICAL: Could not identify columns. Have: {df.columns.tolist()}")
                return

        print(f"Mapping: District='{dist_col}', Name='{name_col}', Phone='{phone_col}'")
        
        data_to_insert = []
        for _, row in df.iterrows():
            d = str(row[dist_col]).strip().title()
            n = str(row[name_col]).strip()
            p = str(row[phone_col]).strip()
            # Basic validation
            if len(d) > 2 and len(n) > 2:
                data_to_insert.append((d, n, p))
        
        cursor.executemany("INSERT INTO police_stations (district, station_name, phone) VALUES (?, ?, ?)", data_to_insert)
        conn.commit()
        print(f"Successfully imported {len(data_to_insert)} stations.")
        
    except Exception as e:
        print(f"Import failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == '__main__':
    import_data()
