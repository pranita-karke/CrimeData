
import sqlite3

def debug_matching():
    conn = sqlite3.connect('crime_data.db')
    conn.row_factory = sqlite3.Row
    
    print("=== SEARCHING FOR 'SAMANA' FIR ===")
    fir = conn.execute("SELECT * FROM firs WHERE full_name LIKE '%samana%'").fetchone()
    if not fir:
        print("CRITICAL: FIR with name 'samana' NOT FOUND in DB.")
        # Print all to see what's there
        print("Dumping last 5 FIRs:")
        firs = conn.execute("SELECT id, full_name, police_station FROM firs ORDER BY id DESC LIMIT 5").fetchall()
        for f in firs:
            print(f"  #{f['id']} - Name: {f['full_name']} - Station: '{f['police_station']}'")
        conn.close()
        return

    print(f"FOUND FIR: ID={fir['id']}, Station='{fir['police_station']}'")
    fir_station = fir['police_station']

    print("\n=== SEARCHING FOR USERS MATCHING 'HANUMAN' ===")
    users = conn.execute("SELECT username, police_station FROM users WHERE role='police' AND police_station LIKE '%hanuman%'").fetchall()
    
    if not users:
        print("CRITICAL: No Police User found with station matching 'hanuman'. Dumping all police users:")
        all_users = conn.execute("SELECT username, police_station FROM users WHERE role='police'").fetchall()
        for u in all_users:
            print(f"  User: {u['username']} - Station: '{u['police_station']}'")
            
    for u in users:
        session_station = u['police_station']
        print(f"\nCreated User Session: '{session_station}'")
        
        # --- REPLICATE APP.PY LOGIC ---
        ignore_words = ["metropolitan", "police", "station", "range", "office", "area", "apo", "of", "woda", "ward", "chowki", "post", "circle", "sector", "beat"]
        clean_session = session_station.lower()
        for word in ignore_words:
            clean_session = clean_session.replace(word, "")
        clean_session = clean_session.strip()
        
        print(f"  Cleaned Session Name: '{clean_session}'")
        
        # Check against FIR Station
        # 1. LIKE
        match_1 = session_station.lower() in fir_station.lower() # approximation of LIKE %session%
        
        # 2. Reverse
        match_2 = fir_station.lower() in session_station.lower()
        
        # 3. Fuzzy (Clean)
        match_3 = clean_session in fir_station.lower()
        
        print(f"  Match 1 (Direct): {match_1}")
        print(f"  Match 2 (Reverse): {match_2}")
        print(f"  Match 3 (Fuzzy '{clean_session}' in '{fir_station.lower()}'): {match_3}")
        
    conn.close()

if __name__ == "__main__":
    debug_matching()
