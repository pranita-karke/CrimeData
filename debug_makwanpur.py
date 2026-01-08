import sqlite3

db_path = 'crime_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Searching for districts starting with 'M'...")
cursor.execute("SELECT DISTINCT district FROM police_stations WHERE district LIKE 'M%'")
rows = cursor.fetchall()
for row in rows:
    print(f"Found: {row[0]}")

conn.close()
