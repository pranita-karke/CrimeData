import prediction
import sys

print("Testing prediction for SINDHULI with empty province...", flush=True)
try:
    result = prediction.train_and_predict(target_year="2082", province="", district="SINDHULI")
    print("Result:", result)
except Exception as e:
    print("CRASHED:", e)
    import traceback
    traceback.print_exc()

print("-" * 20)
print("Testing prediction for TAPLEJUNG...", flush=True)
try:
    result = prediction.train_and_predict(target_year="2082", province="", district="TAPLEJUNG")
    print("Result:", result)
except Exception as e:
    print("CRASHED:", e)
