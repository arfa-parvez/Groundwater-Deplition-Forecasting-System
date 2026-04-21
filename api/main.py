import os
import logging
import sqlite3
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from passlib.context import CryptContext
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv(override=True)

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
gemini_available = False

if GEMINI_API_KEY and GEMINI_API_KEY != "your_google_gemini_api_key_here":
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_available = True
        print("Gemini API configured successfully")
    except Exception as e:
        print(f"Failed to configure Gemini: {e}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
API_KEY = os.getenv("API_KEY", "default-insecure-key")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == API_KEY:
        return api_key
    raise HTTPException(status_code=403, detail="Could not validate credentials")

from pydantic import BaseModel
import pandas as pd
import numpy as np
import datetime
import random

# --- DB & Auth Setup ---
os.makedirs('data', exist_ok=True)
db_conn = sqlite3.connect('data/users.db', check_same_thread=False)
cursor = db_conn.cursor()

# Drop existing table to avoid schema issues
cursor.execute("DROP TABLE IF EXISTS users")
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        email TEXT UNIQUE,
        password_hash TEXT,
        created_at TEXT,
        last_login TEXT,
        pref_region TEXT
    )
''')
db_conn.commit()

app = FastAPI(title="AquaGuard AI API", version="1.0")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class RegisterUser(BaseModel):
    username: str
    email: str
    password: str

class LoginUser(BaseModel):
    username: str
    password: str

class UpdatePassword(BaseModel):
    username: str
    old_password: str
    new_password: str

class UpdatePref(BaseModel):
    username: str
    pref_region: str

@app.post("/auth/signup")
def signup(user: RegisterUser):
    now = datetime.datetime.now().isoformat()
    hashed_pw = pwd_context.hash(user.password)
    try:
        cursor.execute("INSERT INTO users (username, email, password_hash, created_at, last_login, pref_region) VALUES (?, ?, ?, ?, ?, ?)", 
                       (user.username, user.email, hashed_pw, now, now, ""))
        db_conn.commit()
        return {"status": "success", "token": API_KEY}
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail="Username or email already exists.")

@app.post("/auth/login")
def login(user: LoginUser):
    cursor.execute("SELECT password_hash, pref_region FROM users WHERE username=?", (user.username,))
    record = cursor.fetchone()
    if not record:
        raise HTTPException(status_code=400, detail="Invalid username or password.")
        
    if not pwd_context.verify(user.password, record[0]):
        raise HTTPException(status_code=400, detail="Invalid username or password.")
        
    now = datetime.datetime.now().isoformat()
    cursor.execute("UPDATE users SET last_login=? WHERE username=?", (now, user.username))
    db_conn.commit()
    
    return {"status": "success", "token": API_KEY, "pref_region": record[1]}

@app.post("/auth/update-password")
def update_password(data: UpdatePassword, api_key: str = Depends(get_api_key)):
    cursor.execute("SELECT password_hash FROM users WHERE username=?", (data.username,))
    record = cursor.fetchone()
    if not record or not pwd_context.verify(data.old_password, record[0]):
        raise HTTPException(status_code=400, detail="Invalid credentials.")
        
    new_hash = pwd_context.hash(data.new_password)
    cursor.execute("UPDATE users SET password_hash=? WHERE username=?", (new_hash, data.username))
    db_conn.commit()
    return {"status": "success", "message": "Password updated securely."}

@app.post("/auth/update-pref")
def update_pref(data: UpdatePref, api_key: str = Depends(get_api_key)):
    cursor.execute("UPDATE users SET pref_region=? WHERE username=?", (data.pref_region, data.username))
    db_conn.commit()
    return {"status": "success"}

class UserInput(BaseModel):
    region: str
    season: str
    crop_type: str
    rainfall_mm: float
    rainfall_trend_mm: float
    temperature_c: float
    borewell_dependency: float
    
class ChatbotRequest(BaseModel):
    question: str

@app.get("/health")
def health_check():
    return {"status": "ok", "gemini_available": gemini_available}

@app.post("/predict")
def predict_status(data: UserInput, api_key: str = Depends(get_api_key)):
    # Calculate risk score
    risk_score = 0
    
    if data.rainfall_mm < data.rainfall_trend_mm:
        risk_score += 30
    if data.borewell_dependency > 80:
        risk_score += 40
    elif data.borewell_dependency > 60:
        risk_score += 20
    if data.crop_type in ["Rice", "Sugarcane"]:
        risk_score += 25
    if data.temperature_c > 35:
        risk_score += 20
    
    if risk_score >= 60:
        risk = "High"
        status = "Critical - Immediate action required"
    elif risk_score >= 30:
        risk = "Moderate"
        status = "Watch - Monitor closely"
    else:
        risk = "Safe"
        status = "Normal - Continue current practices"
    
    reason = []
    if data.rainfall_mm < data.rainfall_trend_mm:
        reason.append(f"Rainfall deficit ({data.rainfall_mm}mm vs {data.rainfall_trend_mm}mm)")
    if data.borewell_dependency > 60:
        reason.append(f"High borewell dependency ({data.borewell_dependency}%)")
    if data.crop_type in ["Rice", "Sugarcane"]:
        reason.append(f"Water-intensive crop '{data.crop_type}'")
        
    explanation = " | ".join(reason) if reason else "Conditions are within normal ranges"

    crop_suitability = {
        "temperature_suitable": data.temperature_c < 35 and data.temperature_c > 15,
        "rainfall_suitable": data.rainfall_mm > 50,
        "suitability_score": max(0, min(100, 100 - risk_score)),
        "recommended_crops": ["Millets", "Sorghum", "Pulses", "Groundnut", "Cotton"] if risk_score > 50 else ["Rice", "Wheat", "Maize", "Sugarcane", "Soybeans"]
    }

    return {
        "status": status,
        "risk": risk,
        "risk_score": risk_score,
        "explanation": explanation,
        "crop_suitability": crop_suitability
    }

@app.post("/forecast")
def fetch_forecast(data: UserInput, api_key: str = Depends(get_api_key)):
    # Generate realistic forecast values
    base_depth = 35 + (data.borewell_dependency / 100) * 25
    rainfall_impact = max(-15, min(15, (data.rainfall_trend_mm - data.rainfall_mm) / 15))
    
    groundwater = {
        "1_month": round(max(20, base_depth + rainfall_impact * 0.5 + random.uniform(-3, 3)), 1),
        "3_months": round(max(25, base_depth + rainfall_impact * 1.5 + random.uniform(-5, 5)), 1),
        "1_year": round(max(30, base_depth + rainfall_impact * 3 + random.uniform(-8, 8)), 1)
    }
    
    rainfall = {
        "1_month": round(max(0, data.rainfall_mm * 0.85 + random.uniform(-15, 15)), 1),
        "3_months": round(max(0, data.rainfall_mm * 0.7 + random.uniform(-25, 25)), 1),
        "1_year": round(max(0, data.rainfall_mm * 0.55 + random.uniform(-35, 35)), 1)
    }
    
    temperature = {
        "1_month": round(data.temperature_c + random.uniform(-2, 2), 1),
        "3_months": round(data.temperature_c + random.uniform(1, 3), 1),
        "1_year": round(data.temperature_c + random.uniform(2, 5), 1)
    }
    
    return {"forecasts": {"groundwater": groundwater, "rainfall": rainfall, "temperature": temperature}}

@app.post("/recommend")
def get_recommendation(data: UserInput, api_key: str = Depends(get_api_key)):
    pred_res = predict_status(data, api_key)
    risk = pred_res["risk"]
    
    recommendations = {
        "High": [
            "🚨 IMMEDIATE: Stop all non-essential water usage",
            "💧 Switch to drip irrigation (saves 50% water)",
            "🌾 Plant drought-resistant millets or sorghum",
            "📊 Monitor groundwater levels daily",
            "🌧️ Implement rainwater harvesting urgently"
        ],
        "Moderate": [
            "⚠️ Reduce irrigation by 25-30%",
            "💧 Install soil moisture sensors",
            "🔄 Rotate with less water-intensive crops",
            "📈 Apply mulching to retain moisture",
            "💦 Irrigate during early morning or evening"
        ],
        "Safe": [
            "✅ Continue current irrigation practices",
            "💧 Maintain regular water level monitoring",
            "🌧️ Expand rainwater harvesting capacity",
            "📊 Keep water usage records",
            "🌱 Good time for water-intensive crops"
        ]
    }
    
    return {"recommendations": recommendations.get(risk, recommendations["Safe"])}

@app.post("/alert")
def generate_alerts(data: UserInput, api_key: str = Depends(get_api_key)):
    pred_res = predict_status(data, api_key)
    risk = pred_res["risk"]
    
    alerts = {
        "High": {"alert": True, "level": "CRITICAL", "message": "⚠️ CRITICAL: Severe water scarcity! Immediate action required!"},
        "Moderate": {"alert": True, "level": "WARNING", "message": "⚡ WARNING: Water levels declining. Reduce usage by 30%"},
        "Safe": {"alert": False, "level": "NORMAL", "message": "✅ Conditions normal. Continue regular monitoring"}
    }
    return alerts.get(risk, alerts["Safe"])

@app.post("/chatbot")
def chatbot_reply(req: ChatbotRequest, api_key: str = Depends(get_api_key)):
    q = req.question.lower()
    
    responses = {
        "rainfall": "🌧️ **Rainfall Management Tips:**\n\n• Install rain gauges to measure daily rainfall\n• Create farm ponds to store excess rainwater\n• Use drip irrigation during dry spells\n• Practice mulching to retain soil moisture\n• Consider contour farming to reduce runoff\n• Build check dams in low-lying areas\n\n**Best practices:** Harvest every drop of rainwater through rooftop harvesting and farm ponds. One inch of rain on 1 acre gives ~27,000 gallons of water!",
        
        "groundwater": "💧 **Groundwater Management:**\n\n• Monitor water levels weekly using a water level indicator\n• Install recharge pits to replenish groundwater\n• Limit borewell pumping to 4-6 hours/day\n• Maintain at least 20 feet of water column\n• Create percolation tanks in your farm\n• Use rainwater to recharge borewells\n\n**Warning:** If water level drops below 30 feet, reduce pumping immediately!",
        
        "crop": "🌾 **Best Crops for Dry Regions:**\n\n**Drought-resistant crops (40-60% less water):**\n• Millets (Jowar, Bajra, Ragi) - 350mm water\n• Sorghum - 400mm water  \n• Pulses (Tur, Moong, Chana) - 350mm water\n• Oilseeds (Groundnut, Sunflower) - 400mm water\n• Cotton (Bt varieties) - 500mm water\n\n**Water-intensive crops to avoid:** Rice (1200mm), Sugarcane (1800mm)\n\n**Tip:** Rotate crops and use intercropping for better yields!",
        
        "drought": "🏜️ **During Drought Conditions:**\n\n• Prioritize high-value, short-duration crops\n• Use 50% less water with drip irrigation\n• Apply hydrogels or coir pith to soil\n• Harvest every drop of rainwater\n• Consider leaving fallow land for next season\n• Use sprinkler irrigation at night only\n• Apply anti-transpirants to reduce water loss",
        
        "temperature": "🌡️ **High Temperature Management:**\n\n• Use shade nets (40-50% shade) for vegetables\n• Increase irrigation frequency but reduce quantity\n• Apply kaolin clay on leaves (sunburn protection)\n• Plant wind breaks (trees/shrubs)\n• Schedule farming: 6-9 AM or 5-7 PM\n• Use white plastic mulch (reflects heat)\n• Grow heat-tolerant varieties\n\n**Critical:** When temperature > 38°C, stop fertilizer application!",
        
        "water": "💧 **Water Conservation Techniques:**\n\n**Most Effective Methods:**\n1. Drip irrigation - saves 50-70% water\n2. Mulching - reduces evaporation by 70%\n3. Rainwater harvesting - collect 100% runoff\n4. Contour farming - prevents runoff\n5. Cover cropping - improves soil moisture\n6. Sprinkler irrigation - saves 30-40% water\n\n**Pro tip:** Water at sunrise or sunset to reduce evaporation loss by 30%!",
        
        "fertilizer": "🌱 **Efficient Fertilizer Use:**\n\n• Apply during cool hours (6-9 AM)\n• Use slow-release fertilizers\n• Incorporate organic matter (compost/vermicompost)\n• Practice fertigation through drip systems\n• Conduct soil testing every 6 months\n• Use green manure crops (Sunhemp, Dhaincha)\n• Apply jeevamrutha (200L/acre weekly)",
        
        "soil": "🪨 **Soil Health Improvement:**\n\n• Add organic manure (5 tons/acre/year)\n• Practice crop rotation (cereals → legumes)\n• Grow green manure crops\n• Apply mulching (straw/plastic)\n• Maintain soil pH between 6.0-7.5\n• Conduct soil testing every 6 months\n• Use bio-fertilizers (Rhizobium, PSB, Azotobacter)\n• Practice minimum tillage",
        
        "irrigation": "💦 **Efficient Irrigation Methods:**\n\n**By efficiency:**\n• Drip irrigation: 90% efficiency (Best!)\n• Sprinkler: 70% efficiency\n• Furrow: 60% efficiency  \n• Flood: 40% efficiency (Avoid!)\n\n**Schedule tips:**\n• Water at sunrise or sunset\n• Apply deficit irrigation (20-30% less)\n• Install moisture sensors\n• Follow 'more crop per drop' principle\n• Use tensiometers for timing",
        
        "borewell": "⛲ **Borewell Management:**\n\n• Limit pumping to 4-6 hours/day\n• Maintain 20 feet water column minimum\n• Install recharge shafts around borewell\n• Monitor water quality quarterly\n• Annual pump maintenance\n• Install water level indicator\n• Create rainwater recharge pits\n• Don't pump during summer afternoons",
        
        "organic": "🌿 **Organic Farming Tips:**\n\n**Essential inputs:**\n• Vermicompost: 2-3 tons/acre\n• Farmyard manure: 10 tons/acre\n• Jeevamrutha: 200L/acre weekly\n• Panchagavya: 3% foliar spray\n• Neem cake: 200 kg/acre\n\n**Benefits:**\n• 30% lower input costs\n• 20% higher market price\n• Better soil health\n• Groundwater protection",
        
        "default": "🤖 **I'm AquaGuard AI, your agricultural expert!**\n\nI can help you with:\n\n🌧️ **Rainfall** - Management, harvesting, forecasting\n💧 **Groundwater** - Conservation, recharge, monitoring  \n🌾 **Crops** - Selection for dry regions, drought-resistant varieties\n🌡️ **Temperature** - Heat stress management, crop protection\n💦 **Irrigation** - Drip, sprinkler, scheduling, efficiency\n🌱 **Soil** - Health improvement, organic farming\n⛲ **Borewell** - Maintenance, recharge, troubleshooting\n\n**Just ask me anything about farming, water management, or crop cultivation!**"
    }
    
    for key, response in responses.items():
        if key in q and key != "default":
            return {"reply": response}
    
    return {"reply": responses["default"]}