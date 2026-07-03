import sqlite3

def get_db_connection():
    conn = sqlite3.connect('crime_data.db')
    conn.row_factory = sqlite3.Row
    return conn

conn = get_db_connection()
print("--- USERS ---")
users = conn.execute("SELECT username, role, police_station, district FROM users WHERE username LIKE '%alisa%' OR username LIKE '%samana%'").fetchall()
for u in users:
    print(f"User: {u['username']} | Role: {u['role']} | Dist: '{u['district']}' | Stn: '{u['police_station']}'")

print("\n--- ALERTS ---")
alerts = conn.execute("SELECT id, district, message, status, accepted_by FROM alerts").fetchall()
if not alerts:
    print("No alerts found.")
for a in alerts:
    print(f"ID: {a['id']} | Dist: '{a['district']}' | Status: {a['status']} | Accept: {a['accepted_by']}")

conn.close()
