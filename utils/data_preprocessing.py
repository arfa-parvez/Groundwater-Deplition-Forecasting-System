import pandas as pd
import numpy as np

def clean_data(df):
    """
    Handle missing values and outliers if any exist in the real/mock data.
    """
    # Fill missing numerics with median
    num_cols = df.select_dtypes(include=[np.number]).columns
    df[num_cols] = df[num_cols].fillna(df[num_cols].median())
    
    # Fill missing categoricals with mode
    cat_cols = df.select_dtypes(include=['object']).columns
    for col in cat_cols:
        df[col] = df[col].fillna(df[col].mode()[0])
        
    return df

def feature_engineering(df):
    """
    Adds required columns: Rainfall trends, depletion rate, crop water usage proxy, seasonal encoding
    """
    df = df.copy()
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
    # Sort for time-based features
    df = df.sort_values(by=['Region', 'Date']).reset_index(drop=True)
    
    # 1. Seasonal Encoding
    # Assuming standard India seasons: Winter(Jan,Feb), Summer(Mar-May), Monsoon(Jun-Sep), Post-Monsoon(Oct-Dec)
    months = df['Date'].dt.month
    conditions = [
        months.isin([1, 2]),
        months.isin([3, 4, 5]),
        months.isin([6, 7, 8, 9]),
        months.isin([10, 11, 12])
    ]
    seasons = ['Winter', 'Summer', 'Monsoon', 'Post_Monsoon']
    df['Season'] = np.select(conditions, seasons, default='Unknown')
    
    # 2. Crop Water Usage Proxy
    # Map high, medium, low proxy value
    crop_usage_map = {
        "Sugarcane": 3,
        "Rice": 3,
        "Wheat": 2,
        "Cotton": 2,
        "Millets": 1
    }
    df['Crop_Water_Proxy'] = df['Crop_Type'].map(crop_usage_map).fillna(1)
    
    # 3. Rainfall Trends (Rolling 3 periods if frequent data, we'll use diff/shift based on region)
    df['Rainfall_Trend'] = df.groupby('Region')['Rainfall_mm'].shift(1)
    df['Rainfall_Trend'] = df['Rainfall_Trend'].fillna(df['Rainfall_mm'])
    
    # 4. Depletion Rate (difference from previous timestep)
    df['Prev_Level'] = df.groupby('Region')['Groundwater_Level'].shift(1)
    df['Prev_Level'] = df['Prev_Level'].fillna(df['Groundwater_Level'])
    
    # Negative depletion means level decreased (water recovered from deeper), Positive means depth increased (water depleted)
    df['Depletion_Rate'] = df['Groundwater_Level'] - df['Prev_Level']
    
    # Status Tagging (Increase, Stable, Decrease status mapping based on rate)
    # Note: Depth increasing means water decreasing.
    def get_status(rate):
        if rate > 0.5: # Depth increased -> Water Decrease
            return "Decrease"
        elif rate < -0.5: # Depth decreased -> Water Increase
            return "Increase"
        else:
            return "Stable"
    df['Status'] = df['Depletion_Rate'].apply(get_status)

    # Risk Rating
    def get_risk(level):
        if level > 120:
            return "High"
        elif level > 105:
            return "Moderate"
        else:
            return "Safe"
            
    df['Risk'] = df['Groundwater_Level'].apply(get_risk)

    df.drop(columns=['Prev_Level'], inplace=True)
    return df

def preprocess_for_ml(df):
    """
    Returns features (X) and targets (y_status, y_risk, y_level)
    Ready for sklearn models
    """
    # Create copy
    data = clean_data(df)
    data = feature_engineering(data)
    
    # Encoding categorical
    data = pd.get_dummies(data, columns=['Region', 'Crop_Type', 'Season'], drop_first=True)
    
    # X contains numerical values. Drop Date, Targets.
    features = data.drop(columns=['Date', 'Groundwater_Level', 'Status', 'Risk'])
    
    # Fill NAs introduced by shifting
    features = features.fillna(0)
    
    y_status = data['Status']
    y_risk = data['Risk']
    y_level = data['Groundwater_Level']
    
    return features, y_status, y_risk, y_level, data
