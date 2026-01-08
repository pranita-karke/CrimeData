
import sqlite3

def check_names():
    conn = sqlite3.connect('crime_data.db')
    conn.row_factory = sqlite3.Row
    
    print("=== FIR STATIONS ===")
    firs = conn.execute("SELECT id, full_name, police_station FROM firs ORDER BY id DESC LIMIT 5").fetchall()
    for f in firs:
        print(f"FIR {f['id']}: '{f['police_station']}'")

    print("\n=== USER STATIONS ===")
    users = conn.execute("SELECT username, police_station FROM users WHERE role='police'").fetchall()
    for u in users:
        print(f"User {u['username']}: '{u['police_station']}'")

    conn.close()

if __name__ == "__main__":
    check_names()
