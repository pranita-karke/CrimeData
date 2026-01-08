import requests

url = 'http://127.0.0.1:5001/api/create_alert'
# Simulate a request WITHOUT cookies (session) to see fallback
print("--- TEST 1: No Session ---")
try:
    res = requests.post(url, json={'district': 'Kathmandu', 'message': 'Test Alert No Session'})
    print(res.json())
except Exception as e:
    print(e)
