import sqlite3

conn = sqlite3.connect('crime_data.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("--- SCHEMA BEFORE ---")
cols = cursor.execute("PRAGMA table_info(alerts)").fetchall()
col_names = [c['name'] for c in cols]
print(col_names)

if 'sender_name' not in col_names:
    print("ADDING sender_name COLUMN...")
    cursor.execute("ALTER TABLE alerts ADD COLUMN sender_name TEXT")
    conn.commit()
else:
    print("Column sender_name ALREADY EXISTS.")

print("--- SCHEMA AFTER ---")
cols = cursor.execute("PRAGMA table_info(alerts)").fetchall()
print([c['name'] for c in cols])

conn.close()
