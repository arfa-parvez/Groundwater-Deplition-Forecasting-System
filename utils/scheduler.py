import time
from datetime import datetime
import random
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api.main import predict_status, UserInput

def scheduled_job():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running scheduled check...")
    
    # Mocking standard farmer data to represent random samples
    regions = ["Kolar", "Tumkur", "Chitradurga", "Ballari", "Hubli"]
    sample_data = UserInput(
        region=random.choice(regions),
        season="Summer",
        crop_type="Rice",
        rainfall_mm=random.uniform(10, 50),
        rainfall_trend_mm=80,
        temperature_c=random.uniform(35, 42),
        borewell_dependency=random.uniform(70, 100)
    )
    
    try:
        res = predict_status(sample_data)
        risk = res['risk']
        print(f"Region: {sample_data.region} -> Risk: {risk}")
        
        if risk == "High":
            print(f"🚨 AUTO-ALERT: High risk detected for {sample_data.region}! Sending SMS to registered farmers.")
    except Exception as e:
        print("Error connecting or models not trained.")
        
if __name__ == "__main__":
    print("Starting Automated Scheduler...")
    # Run loop 3 times for demo purposes
    for i in range(3):
        scheduled_job()
        time.sleep(2)
    print("Scheduler run completed.")
