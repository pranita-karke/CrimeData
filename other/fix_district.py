import sqlite3

conn = sqlite3.connect('crime_data.db')
cursor = conn.cursor()

# Check current state
print("--- BEFORE ---")
rows = cursor.execute("SELECT username, district FROM users WHERE username LIKE '%alisa%'").fetchall()
for r in rows:
    print(r)

# Update
print("--- UPDATING ---")
cursor.execute("UPDATE users SET district = 'Kathmandu' WHERE username LIKE '%alisa%'")
conn.commit()

# Check after
print("--- AFTER ---")
rows = cursor.execute("SELECT username, district FROM users WHERE username LIKE '%alisa%'").fetchall()
for r in rows:
    print(r)

conn.close()
