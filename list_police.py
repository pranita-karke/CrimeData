import sqlite3

conn = sqlite3.connect('crime_data.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("--- POLICE USERS ---")
users = cursor.execute("SELECT username, district, police_station FROM users WHERE role='police'").fetchall()
for u in users:
    print(f"User: {u['username']} | Dist: '{u['district']}' | Stn: '{u['police_station']}'")

conn.close()
