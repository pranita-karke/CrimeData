import sqlite3
conn = sqlite3.connect('crime_data.db')
row = conn.execute("SELECT sender_name FROM alerts ORDER BY created_at DESC LIMIT 1").fetchone()
print(f"NAME: '{row[0]}'")
conn.close()
