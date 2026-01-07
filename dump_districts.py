import sqlite3

conn = sqlite3.connect('crime_data.db')
cursor = conn.cursor()

rows = cursor.execute("SELECT DISTINCT district FROM main_crime ORDER BY district").fetchall()
with open("districts.txt", "w", encoding="utf-8") as f:
    for r in rows:
        val = r[0]
        f.write(f"'{val}'\n")

print(f"Dumped {len(rows)} districts to districts.txt")
conn.close()
