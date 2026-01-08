import requests
import sys

# 1. Check DB first
import sqlite3
conn = sqlite3.connect('crime_data.db')
conn.row_factory = sqlite3.Row
rows = conn.execute("SELECT id, sender_name FROM alerts ORDER BY created_at DESC LIMIT 1").fetchall()
print("--- DB LATEST ALERT ---")
if not rows:
    print("No alerts found.")
else:
    for r in rows:
        print(f"ID:{r['id']} | Name: '{r['sender_name']}'")
conn.close()

# 2. Check API Response (Login as Alise)
s = requests.Session()
login_url = 'http://127.0.0.1:5001/login'
# Using alise credential
res = s.post(login_url, data={'username': 'alise@gmail.com', 'password': 'password123'}) # Assuming pw

alerts_url = 'http://127.0.0.1:5001/api/my_alerts'
try:
    r = s.get(alerts_url)
    data = r.json()
    print("\n--- API RESPONSE ---")
    if isinstance(data, list) and len(data) > 0:
        a = data[0]
        print(f"Keys: {list(a.keys())}")
        print(f"Sender Name Value: '{a.get('sender_name')}'")
    else:
        print("API returned empty list or error:", data)
except Exception as e:
    print("API Request failed:", e)
