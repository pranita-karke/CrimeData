import sqlite3

conn = sqlite3.connect('crime_data.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("--- WALTER DETAILS ---")
user = cursor.execute("SELECT * FROM users WHERE username LIKE '%walter%'").fetchone()
if user:
    print(f"Username: '{user['username']}'")
    print(f"Full Name: '{user['full_name']}'")
    print(f"Role: '{user['role']}'")
    print(f"District: '{user['district']}'")
    print(f"Station: '{user['police_station']}'")
else:
    print("User 'walter' not found.")

conn.close()
