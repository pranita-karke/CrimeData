import requests
import json

def check_keys():
    try:
        # Check Main Crime Data Keys
        r1 = requests.get('http://127.0.0.1:5001/api/crime/main')
        d1 = r1.json()
        if d1 and len(d1) > 0:
            print("MAIN CRIME KEYS:", list(d1[0].keys()))
        else:
            print("MAIN CRIME DATA EMPTY")

        # Check Police Data Keys
        r2 = requests.get('http://127.0.0.1:5001/api/police')
        d2 = r2.json()
        if d2 and len(d2) > 0:
            print("POLICE DATA KEYS:", list(d2[0].keys()))
        else:
            print("POLICE DATA EMPTY")

    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    check_keys()
