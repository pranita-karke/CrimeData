
import sqlite3

def check_fir_7123():
    conn = sqlite3.connect('crime_data.db')
    conn.row_factory = sqlite3.Row
    
    print("\n=== FIR #7123 ===")
    fir = conn.execute("SELECT * FROM firs WHERE id=7123").fetchone()
    if fir:
        print(f"ID: {fir['id']}")
        print(f"Full Name: '{fir['full_name']}'")
        print(f"Station (Raw): '{fir['police_station']}'")
        print(f"District: '{fir['district']}'")
    else:
        print("FIR #7123 not found. Dumping last 3 FIRs:")
        recents = conn.execute("SELECT id, full_name, police_station FROM firs ORDER BY id DESC LIMIT 3").fetchall()
        for r in recents:
            print(f"  #{r['id']} ({r['full_name']}): '{r['police_station']}'")

    print("\n=== USER 'Shiwani' ===")
    user = conn.execute("SELECT * FROM users WHERE full_name LIKE '%Shiwani%' OR username LIKE '%Shiwani%'").fetchone()
    if user:
        print(f"Username: {user['username']}")
        print(f"Role: {user['role']}")
        print(f"Station (Raw): '{user['police_station']}'")
    else:
        print("User 'Shiwani' not found.")

    conn.close()

if __name__ == "__main__":
    check_fir_7123()
