import sqlite3
conn = sqlite3.connect('crime_data.db')
cursor = conn.cursor()
rows = cursor.execute("SELECT id, sender_name FROM alerts ORDER BY created_at DESC LIMIT 3").fetchall()
print("LATEST ALERTS:")
for r in rows:
    print(f"ID:{r[0]} Name:{r[1]}")
conn.close()
