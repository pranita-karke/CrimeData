import sqlite3
conn = sqlite3.connect('crime_data.db')
conn.row_factory = sqlite3.Row
rows = conn.execute("SELECT * FROM users WHERE username LIKE '%samana%'").fetchall()
print("--- SAMANA ---")
for r in rows:
    print(f"User: {r['username']} | Name: '{r['full_name']}'")
conn.close()
