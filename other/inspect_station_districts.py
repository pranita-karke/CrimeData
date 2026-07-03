
import sqlite3
import pandas as pd

def check_names():
    # 1. Get Districts from Main Data (Simulated source for /api/districts)
    # The app.py loads main_data from 'crime_data.csv' or similar. 
    # I'll check app.py to see where it comes from, but for now let's just assume I can verify the DB or CSV.
    # Wait, app.py uses pandas to read excel/csv. Let's see if we can just query the DB for police stations first.
    
    conn = sqlite3.connect('crime_data.db')
    cursor = conn.cursor()
    
    print("--- Police Station Districts (DB) ---")
    try:
        stations = cursor.execute("SELECT DISTINCT district FROM police_stations ORDER BY district").fetchall()
        for s in stations:
            print(s[0])
    except Exception as e:
        print(f"Error querying police_stations: {e}")

    conn.close()

if __name__ == "__main__":
    check_names()
