
from app import app
from flask import session

def test_endpoint():
    app.secret_key = 'super_secret_key_for_demo'
    
    with app.test_client() as client:
        # Simulate Login Session
        with client.session_transaction() as sess:
            sess['user_id'] = 2
            sess['role'] = 'police'
            sess['station'] = 'District Police Office (DPO) Ilam' 
            
        print(f"Testing with Station: {sess['station']}")
        
        try:
            res = client.get('/api/my_complaints')
            print(f"Status Code: {res.status_code}")
            if res.status_code != 200:
                print(f"Error Response: {res.get_data(as_text=True)}")
            else:
                print(f"Success! Data: {res.get_json()}")
        except Exception as e:
            print(f"CRASH: {e}")

if __name__ == "__main__":
    test_endpoint()
