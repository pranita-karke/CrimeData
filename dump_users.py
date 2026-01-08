import sqlite3

conn = sqlite3.connect('crime_data.db')
conn.row_factory = sqlite3.Row
rows = conn.execute("SELECT * FROM users").fetchall()
print(f"Total Users: {len(rows)}")
for r in rows:
    print(dict(r))
conn.close()
