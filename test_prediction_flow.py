import requests
import json

BASE_URL = "http://127.0.0.1:5001"

def test_prediction():
    print("Testing Prediction Endpoint...")
    
    # Test 1: Province Only (if supported, or just verify one district)
    payload1 = {
        "year": "2082",
        "province": "Koshi",
        "district": "Bhojpur"
    }
    
    try:
        print(f"Sending Request 1: {payload1}")
        res1 = requests.post(f"{BASE_URL}/api/predict", json=payload1)
        print(f"Response 1 Status: {res1.status_code}")
        print(f"Response 1 Data: {res1.json()}")
    except Exception as e:
        print(f"Request 1 Failed: {e}")

    # Test 2: Different District
    payload2 = {
        "year": "2082",
        "province": "Koshi",
        "district": "Dhankuta"
    }
    
    try:
        print(f"\nSending Request 2: {payload2}")
        res2 = requests.post(f"{BASE_URL}/api/predict", json=payload2)
        print(f"Response 2 Status: {res2.status_code}")
        print(f"Response 2 Data: {res2.json()}")
        
        # Compare results
        if res1.json() == res2.json():
            print("\nNOTE: Results are identical (Expected due to data duplication issue).")
        else:
            print("\nNOTE: Results are different.")
            
    except Exception as e:
        print(f"Request 2 Failed: {e}")

if __name__ == "__main__":
    test_prediction()
