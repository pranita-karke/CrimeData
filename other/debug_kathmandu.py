import sqlite3

conn = sqlite3.connect('crime_data.db')
cursor = conn.cursor()

print("Checking Kathmandu variants...", flush=True)
rows = cursor.execute("SELECT DISTINCT district FROM main_crime WHERE district LIKE '%Kath%'").fetchall()
for r in rows:
    val = r[0]
    print(f"'{val}' (len={len(val)})")

# Also run prediction check
import prediction
print("\n--- Running Prediction Check ---", flush=True)
try:
    res = prediction.train_and_predict("2082", "", "Kathmandu")
    print("Result keys:", res.keys() if 'error' not in res else res)
except Exception as e:
    print("CRASH:", e)
    import traceback
    traceback.print_exc()

conn.close()
