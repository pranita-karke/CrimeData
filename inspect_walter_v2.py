import sqlite3
conn = sqlite3.connect('crime_data.db')
conn.row_factory = sqlite3.Row
u = conn.execute("SELECT * FROM users WHERE username LIKE '%walter%'").fetchone()
if u:
    print(f"U:{u['username']}|R:{u['role']}|D:'{u['district']}'|S:'{u['police_station']}'")
else:
    print("Not found")
conn.close()
