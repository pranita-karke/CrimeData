import pandas as pd
import sqlite3
import os

EXCEL_FILE = 'nepal_gbv_complete_dataset.xlsx'
DB_FILE = 'crime_data.db'

def init_db():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    try:
        xl = pd.ExcelFile(EXCEL_FILE)
        
        # --- Sheet 1: Complete_Data -> main_crime ---
        print("Processing 'Complete_Data'...")
        df_main = xl.parse('Complete_Data')
        df_main.columns = [c.strip().lower().replace(' ', '_') for c in df_main.columns]
        
        cursor.execute('''
            CREATE TABLE main_crime (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year TEXT,
                province TEXT,
                district TEXT,
                crime_type TEXT,
                total_cases INTEGER
            )
        ''')
        df_main.to_sql('main_crime', conn, if_exists='append', index=False)
        
        # --- Sheet 2: Extra -> victim_demographics ---
        print("Processing 'Extra'...")
        df_dem = xl.parse('Extra')
        df_dem.rename(columns={'FY': 'Year'}, inplace=True)
        
        clean_cols = []
        for c in df_dem.columns:
            new_c = c.strip().replace(' ', '_').replace('≤', 'lte_').replace('+', '_plus').replace('/', '_')
            clean_cols.append(new_c)
        df_dem.columns = clean_cols
        
        # Add 'id' column
        df_dem.index.name = 'id'
        df_dem.reset_index(inplace=True) 
        df_dem['id'] = df_dem['id'] + 1 
        
        # Write directly using to_sql (simplest and robust)
        df_dem.to_sql('victim_demographics', conn, if_exists='replace', index=False, dtype={'id': 'INTEGER PRIMARY KEY'})
        
        # --- Sheet 3: Police -> police_performance ---
        print("Processing 'Police'...")
        df_pol = xl.parse('Police')
        df_pol.columns = [c.strip().replace(' ', '_') for c in df_pol.columns]
        
        df_pol.index.name = 'id'
        df_pol.reset_index(inplace=True)
        df_pol['id'] = df_pol['id'] + 1
        
        df_pol.to_sql('police_performance', conn, if_exists='replace', index=False, dtype={'id': 'INTEGER PRIMARY KEY'})
        
        print("Database initialized successfully.")
        
        # Verify
        cursor.execute("SELECT count(*) FROM main_crime")
        print(f"Main Crime rows: {cursor.fetchone()[0]}")
        cursor.execute("SELECT count(*) FROM victim_demographics")
        print(f"Demographics rows: {cursor.fetchone()[0]}")
        cursor.execute("SELECT count(*) FROM police_performance")
        print(f"Police rows: {cursor.fetchone()[0]}")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == '__main__':
    init_db()
