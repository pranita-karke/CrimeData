import sqlite3

conn = sqlite3.connect('crime_data.db')
cursor = conn.cursor()

patterns = ['%Kav%', '%Tan%', '%Nawal%', '%Rukum%'] # Rukum is also often split
print("Checking for district name variations...", flush=True)

for p in patterns:
    print(f"\n--- Matching '{p}' ---")
    rows = cursor.execute("SELECT DISTINCT district FROM main_crime WHERE district LIKE ?", (p,)).fetchall()
    for r in rows:
        print(r[0])

conn.close()
