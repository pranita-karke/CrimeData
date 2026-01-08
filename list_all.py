import sqlite3
conn = sqlite3.connect('crime_data.db')
conn.row_factory = sqlite3.Row
rows = conn.execute("SELECT id, username, district FROM users").fetchall()
print(f"Count: {len(rows)}")
for r in rows:
    print(f"{r['id']}: {r['username']} ({r['district']})")
conn.close()
