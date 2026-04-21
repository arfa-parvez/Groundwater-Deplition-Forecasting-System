import os
import sys
import pickle
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, mean_squared_error
from prophet import Prophet
import numpy as np

# Adjust path to import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.data_ingestion import generate_mock_data
from utils.data_preprocessing import preprocess_for_ml

def train_classification_models(X, y_status, y_risk):
    X_train, X_test, y_train, y_test = train_test_split(X, y_risk, test_size=0.2, random_state=42)
    
    # Random Forest (Main)
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    rf_preds = rf.predict(X_test)
    print(f"Random Forest Risk Accuracy: {accuracy_score(y_test, rf_preds):.2f}")
    
    # XGBoost (Comparison)
    # Require encoding labels to int for xgboost
    label_mapping = {label: idx for idx, label in enumerate(y_train.unique())}
    y_train_encoded = y_train.map(label_mapping)
    y_test_encoded = y_test.map(label_mapping)
    
    xgb = XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', random_state=42)
    xgb.fit(X_train, y_train_encoded)
    xgb_preds = xgb.predict(X_test)
    print(f"XGBoost Risk Accuracy: {accuracy_score(y_test_encoded, xgb_preds):.2f}")
    
    # Linear Model (Baseline) for Risk
    lr = LogisticRegression(max_iter=1000)
    lr.fit(X_train, y_train)
    
    # Let's save Random Forest as the main Risk model
    with open('models/risk_model.pkl', 'wb') as f:
        pickle.dump(rf, f)
        
    # Classification for Status (Increase/Stable/Decrease)
    y_stat_train, y_stat_test = train_test_split(y_status, test_size=0.2, random_state=42)
    rf_stat = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_stat.fit(X_train, y_stat_train)
    print(f"Random Forest Status Accuracy: {accuracy_score(y_stat_test, rf_stat.predict(X_test)):.2f}")
    
    with open('models/status_model.pkl', 'wb') as f:
        pickle.dump(rf_stat, f)
        
def train_forecasting_models(df):
    """
    Train a Prophet model for a specific region to forecast water levels
    """
    # Assuming Hubli as an example region for forecasting model storage
    region_data = df[df['Region'] == 'Hubli'].copy()
    region_data = region_data.rename(columns={'Date': 'ds', 'Groundwater_Level': 'y'})
    
    m = Prophet(daily_seasonality=False)
    m.fit(region_data[['ds', 'y']])
    
    with open('models/forecast_model_hubli.pkl', 'wb') as f:
        pickle.dump(m, f)
    print("Prophet Forecast model saved for Hubli")

def main():
    os.makedirs('data', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    
    data_path = 'data/groundwater_data.csv'
    if not os.path.exists(data_path):
         print("Generating Mock Data...")
         df = generate_mock_data(save_path=data_path)
    else:
         df = pd.read_csv(data_path)

    print("Preprocessing data...")
    X, y_status, y_risk, y_level, processed_df = preprocess_for_ml(df)
    
    print("Training Classification Models...")
    train_classification_models(X, y_status, y_risk)
    
    print("Training Forecasting Models...")
    train_forecasting_models(df)

if __name__ == '__main__':
    main()
