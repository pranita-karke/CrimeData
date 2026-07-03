import sqlite3

conn = sqlite3.connect('crime_data.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("--- POLICE USERS (Alise/Walter) ---")
users = cursor.execute("SELECT username, district FROM users WHERE username LIKE '%alise%' OR username LIKE '%walter%'").fetchall()
for u in users:
    print(f"User: {u['username']} | Dist: '{u['district']}'")

print("\n--- RECENT ALERTS ---")
alerts = cursor.execute("SELECT id, district, message, created_at FROM alerts ORDER BY created_at DESC LIMIT 5").fetchall()
for a in alerts:
    print(f"Alert ID: {a['id']} | Target Dist: '{a['district']}' | Time: {a['created_at']}")

conn.close()
