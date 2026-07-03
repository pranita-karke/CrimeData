import prediction
import json

# Test 1: Compare two districts in Valley
print("\n--- Test 1: Valley / Kathmandu Metropolitan ---")
r1 = prediction.train_and_predict(2082, province="Valley", district="Kathmandu Metropolitan")
print(f"Kathmandu Total: {r1.get('total_predicted_cases')}")

print("\n--- Test 2: Valley / Bhaktapur Metropolitan ---")
r2 = prediction.train_and_predict(2082, province="Valley", district="Bhaktapur Metropolitan")
print(f"Bhaktapur Total: {r2.get('total_predicted_cases')}")

if r1.get('total_predicted_cases') != r2.get('total_predicted_cases'):
    print("\nSUCCESS: Data varies by district.")
else:
    print("\nWARNING: Data identical for different districts (could be data issue or filter bug).")
