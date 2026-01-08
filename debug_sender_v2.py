import sqlite3
conn = sqlite3.connect('crime_data.db')
conn.row_factory = sqlite3.Row
rows = conn.execute("SELECT id, district, sender_name, message, created_at FROM alerts ORDER BY created_at DESC LIMIT 5").fetchall()
print("--- RECENT ALERTS ---")
for r in rows:
    print(f"ID:{r['id']} | Sender:{r['sender_name']} (Type: {type(r['sender_name'])}) | Msg:{r['message']}")
conn.close()
