
import sqlite3

def check_data():
    conn = sqlite3.connect('crime_data.db')
    conn.row_factory = sqlite3.Row
    
    print("\n=== USERS (Police) ===")
    users = conn.execute("SELECT username, full_name, role, police_station, district FROM users WHERE role='police'").fetchall()
    for u in users:
        print(f"User: {u['username']}, Station: '{u['police_station']}', District: '{u['district']}'")
        
    print("\n=== FIRS (All) ===")
    firs = conn.execute("SELECT id, full_name, police_station, district, status FROM firs").fetchall()
    for f in firs:
        print(f"FIR #{f['id']}: Station: '{f['police_station']}', District: '{f['district']}'")
        
    print("\n=== MATCH TEST ===")
    # Simulate the logic for each police user against each FIR
    for u in users:
        station_name = u['police_station']
        if not station_name: continue
        
        clean_station = station_name.lower().replace("metropolitan", "").replace("police", "").replace("station", "").replace("range", "").replace("office", "").replace("area", "").strip()
        
        print(f"\nChecking for Police User '{u['username']}' (Station: '{station_name}')...")
        print(f"Cleaned Name: '{clean_station}'")
        
        query = """
            SELECT id, police_station FROM firs 
            WHERE 
               police_station LIKE ? COLLATE NOCASE 
               OR ? LIKE ('%' || police_station || '%') COLLATE NOCASE
               OR police_station LIKE ? COLLATE NOCASE
        """
        matches = conn.execute(query, (f"%{station_name}%", station_name, f"%{clean_station}%")).fetchall()
        if matches:
            for m in matches:
                print(f"  -> MATCHED FIR #{m['id']} (FIR Station: '{m['police_station']}')")
        else:
            print("  -> NO MATCHES FOUND")

    conn.close()

if __name__ == "__main__":
    check_data()
