import requests
import json

BASE = "http://127.0.0.1:5001"

def check_structure():
    print("--- MAIN CRIME DATA ---")
    try:
        r = requests.get(f"{BASE}/api/crime/main")
        data = r.json()
        if data:
            print(json.dumps(data[0], indent=2))
        else:
            print("No data returned")
    except Exception as e:
        print(e)
        
    print("\n--- POLICE DATA ---")
    try:
        r = requests.get(f"{BASE}/api/police")
        data = r.json()
        if data:
            print(json.dumps(data[0], indent=2))
        else:
            print("No data returned")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    check_structure()
