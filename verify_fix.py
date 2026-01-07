import requests
import json

BASE_URL = "http://127.0.0.1:5001"

def verify_fix():
    print("Verifying Prediction Fix for Low Data District (Manang)...")
    
    payload = {
        "year": "2082",
        "province": "Gandaki",
        "district": "Manang"
    }
    
    try:
        res = requests.post(f"{BASE_URL}/api/predict", json=payload)
        data = res.json()
        
        print("\nPrediction Result:")
        print(f"Status: {data.get('safety_status')}")
        print(f"Total Predicted: {data.get('total_predicted_cases')}")
        
        rising = data.get('rising_crimes', [])
        print(f"Rising Crimes Count: {len(rising)}")
        
        if data.get('safety_status') == "High Risk (Rising)" and len(rising) == 0:
            print("FAIL: Status is High Risk but Rising Crimes list is empty!")
        elif len(rising) > 0:
            print("SUCCESS: Rising Crimes list is populated.")
            print(f"Top Rising Crime: {rising[0]}")
        else:
            print("NOTE: Status is not High Risk, so empty list is acceptable.")
            
    except Exception as e:
        print(f"Request Failed: {e}")

if __name__ == "__main__":
    verify_fix()
