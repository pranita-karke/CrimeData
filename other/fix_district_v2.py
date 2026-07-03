import sqlite3

conn = sqlite3.connect('crime_data.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("--- SEARCHING FOR ALISE ---")
users = cursor.execute("SELECT * FROM users WHERE username LIKE '%alise%' OR full_name LIKE '%alise%'").fetchall()

if not users:
    print("NO USER FOUND matching 'alisa'. Dumping ALL users to debug:")
    all_users = cursor.execute("SELECT username, full_name FROM users").fetchall()
    for u in all_users:
        print(f"User: {u['username']}, Name: {u['full_name']}")
else:
    for u in users:
        print(f"Found User: {u['username']} (District: '{u['district']}')")
        
    print("--- UPDATING TO 'Kathmandu' ---")
    cursor.execute("UPDATE users SET district = 'Kathmandu' WHERE username = 'walter@gmail.com'")
    conn.commit()
    print(f"Updated {cursor.rowcount} rows.")

conn.close()
