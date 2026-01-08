import requests
import sqlite3
import time

BASE_URL = 'http://127.0.0.1:5001'
s = requests.Session()

# 1. Register New User
username = f"testuser_{int(time.time())}"
print(f"--- REGISTERING {username} ---")
reg_data = {
    'full_name': 'Test User New',
    'username': username + '@gmail.com',
    'password': 'password123',
    'confirm_password': 'password123',
    'role': 'user',
    'district': 'Bhaktapur'
}
r = s.post(f'{BASE_URL}/register', data=reg_data)
print(f"Register Status: {r.status_code}")

# 2. Login
print("--- LOGGING IN ---")
login_data = {'username': username + '@gmail.com', 'password': 'password123'}
r = s.post(f'{BASE_URL}/login', data=login_data)
print(f"Login Status: {r.status_code}")

# 3. Create Alert
print("--- SENDING ALERT ---")
alert_data = {'district': 'Bhaktapur', 'message': 'Test Alert New User'}
r = s.post(f'{BASE_URL}/api/create_alert', json=alert_data)
print(f"Create Alert Status: {r.status_code}")
print(r.json())

# 4. Verify in DB
print("--- VERIFYING DB ---")
conn = sqlite3.connect('crime_data.db')
conn.row_factory = sqlite3.Row
rows = conn.execute("SELECT sender_name, district, message FROM alerts ORDER BY created_at DESC LIMIT 1").fetchall()
for row in rows:
    print(f"Sender: '{row['sender_name']}' | Dist: {row['district']} | Msg: {row['message']}")
conn.close()
