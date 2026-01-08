import sqlite3
conn = sqlite3.connect('crime_data.db')
cursor = conn.cursor()

print("--- DELETING ALERTS ---")
# Optional: could just delete where sender_name is NULL, but user likely wants a clean slate.
cursor.execute("DELETE FROM alerts")
conn.commit()
print(f"Deleted {cursor.rowcount} alerts.")

conn.close()
