
import sqlite3
import pandas as pd

def check_provinces():
    conn = sqlite3.connect('crime_data.db')
    
    print("--- Demographics Provinces ---")
    try:
        # Assuming table name is 'demographics' based on previous context, or I need to find it.
        # Let's check table names first just in case.
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        print("Tables:", [t[0] for t in tables])
        
        # Check demographics if exists
        if ('demographics_data',) in tables: # Might be named differently
             res = conn.execute("SELECT DISTINCT Province FROM demographics_data").fetchall()
             for r in res: print(r[0])
        elif ('victim_demographics',) in tables:
             res = conn.execute("SELECT DISTINCT Province FROM victim_demographics").fetchall()
             for r in res: print(r[0])
             
    except Exception as e:
        print("Error demographics:", e)

    print("\n--- Police Data Provinces ---")
    try:
        if ('police_data',) in tables:
             res = conn.execute("SELECT DISTINCT Region FROM police_data").fetchall() # Sometimes called Region in police data
             for r in res: print(r[0])
        elif ('police_stats',) in tables:
             res = conn.execute("SELECT DISTINCT Province FROM police_stats").fetchall()
             for r in res: print(r[0])
    except Exception as e:
         print("Error police:", e)

    conn.close()

if __name__ == "__main__":
    check_provinces()
