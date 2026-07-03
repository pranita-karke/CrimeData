import sqlite3
import binascii

conn = sqlite3.connect('crime_data.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("--- WALTER ---")
rows = cursor.execute("SELECT username, district, hex(district) as hex_dist FROM users WHERE username LIKE '%walter%'").fetchall()
for r in rows:
    print(f"User: {r['username']}")
    print(f"Dist: '{r['district']}'")
    print(f"Hex:  {r['hex_dist']}")

print("\n--- RECENT ALERT ---")
rows = cursor.execute("SELECT id, district, hex(district) as hex_dist FROM alerts ORDER BY created_at DESC LIMIT 1").fetchall()
for r in rows:
    print(f"Alert ID: {r['id']}")
    print(f"Dist: '{r['district']}'")
    print(f"Hex:  {r['hex_dist']}")

conn.close()
