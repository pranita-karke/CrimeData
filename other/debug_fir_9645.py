
import sqlite3

def check_specific_fir():
    conn = sqlite3.connect('crime_data.db')
    conn.row_factory = sqlite3.Row
    
    print("\n=== FIR #9645 ===")
    fir = conn.execute("SELECT * FROM firs WHERE id=9645").fetchone()
    if fir:
        print(f"ID: {fir['id']}")
        print(f"Station (Raw): '{fir['police_station']}'")
        print(f"District: '{fir['district']}'")
    else:
        print("FIR #9645 not found. Listing recent FIRs:")
        recents = conn.execute("SELECT id, police_station FROM firs ORDER BY id DESC LIMIT 5").fetchall()
        for r in recents:
            print(f"ID: {r['id']}, Station: '{r['police_station']}'")

    print("\n=== POLICE USERS ===")
    users = conn.execute("SELECT username, police_station, district FROM users WHERE role='police'").fetchall()
    for u in users:
        print(f"User: '{u['username']}', Station: '{u['police_station']}'")

    conn.close()

if __name__ == "__main__":
    check_specific_fir()
