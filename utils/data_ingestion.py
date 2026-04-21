import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_mock_data(num_records=5000, save_path="data/groundwater_data.csv"):
    """
    Generate mock dataset for AquaGuard AI project prioritizing
    factors like rainfall, season, crop types, and extraction levels.
    """
    np.random.seed(42)
    start_date = datetime(2018, 1, 1)
    
    dates = [start_date + timedelta(days=np.random.randint(0, 2000)) for _ in range(num_records)]
    dates.sort()
    
    regions = np.random.choice(["Kolar", "Tumkur", "Chitradurga", "Ballari", "Hubli"], num_records)
    
    # Simulate seasons implicitly through months
    months = [d.month for d in dates]
    
    # Rainfall in mm - higher in monsoon (June-September)
    rainfall = []
    for m in months:
        if m in [6, 7, 8, 9]:
            rainfall.append(np.random.uniform(50, 300))
        else:
            rainfall.append(np.random.uniform(0, 50))
            
    temperature = np.random.uniform(20, 42, num_records)
    
    # Crop Type determining Water Usage
    crops = ["Rice", "Wheat", "Sugarcane", "Cotton", "Millets"]
    crop_probs = [0.3, 0.2, 0.2, 0.2, 0.1]
    crop_type = np.random.choice(crops, num_records, p=crop_probs)
    
    # Borewell dependency percentage
    borewell_dependency = np.random.uniform(40, 100, num_records)
    
    # Base groundwater level (meters below ground level - so higher is worse)
    # Let's say baseline is 100m, high water usage crops & low rain increases depth
    
    groundwater_level = []
    base_level = 100.0
    for r, c, dep in zip(rainfall, crop_type, borewell_dependency):
        # Modification factors
        rain_effect = - (r * 0.05)  # Restores water
        crop_effect = {"Rice": 5, "Sugarcane": 6, "Wheat": 3, "Cotton": 2, "Millets": 1}[c]
        dep_effect = dep * 0.05
        
        noise = np.random.normal(0, 2)
        
        current_level = base_level + rain_effect + crop_effect + dep_effect + noise
        groundwater_level.append(current_level)
        
        # Slowly trend base level downward (deeper)
        base_level += 0.005
        
    df = pd.DataFrame({
        "Date": dates,
        "Region": regions,
        "Rainfall_mm": rainfall,
        "Temperature_C": temperature,
        "Crop_Type": crop_type,
        "Borewell_Dependency": borewell_dependency,
        "Groundwater_Level": groundwater_level
    })
    
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    df.to_csv(save_path, index=False)
    print(f"Dataset generated at {save_path} with {num_records} records.")
    return df

if __name__ == "__main__":
    generate_mock_data()
