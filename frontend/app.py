import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from fpdf import FPDF
import os
import datetime
import random
import numpy as np

# Set random seed for consistent results
random.seed(42)
np.random.seed(42)

# =========================================================================
# PDF Generation Function (Fixed)
# =========================================================================
def generate_pdf_report(data):
    """Generate PDF report with error handling"""
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, txt="AquaGuard AI - Water Management Report", ln=1, align='C')
        pdf.ln(10)
        
        # Date
        pdf.set_font("Arial", "", 10)
        date_text = f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        pdf.cell(200, 10, txt=date_text, ln=1, align='R')
        pdf.ln(5)
        
        # Input Parameters
        pdf.set_font("Arial", "B", 12)
        pdf.cell(200, 10, txt="INPUT PARAMETERS", ln=1)
        pdf.set_font("Arial", "", 11)
        
        pdf.cell(200, 8, txt=f"Region: {data['payload']['region']}", ln=1)
        pdf.cell(200, 8, txt=f"Crop: {data['payload']['crop_type']}", ln=1)
        pdf.cell(200, 8, txt=f"Season: {data['payload']['season']}", ln=1)
        pdf.cell(200, 8, txt=f"Rainfall: {data['payload']['rainfall_mm']} mm", ln=1)
        pdf.cell(200, 8, txt=f"Temperature: {data['payload']['temperature_c']}°C", ln=1)
        pdf.cell(200, 8, txt=f"Borewell Dependency: {data['payload']['borewell_dependency']}%", ln=1)
        pdf.ln(5)
        
        # Results
        pdf.set_font("Arial", "B", 12)
        pdf.cell(200, 10, txt="ANALYSIS RESULTS", ln=1)
        pdf.set_font("Arial", "", 11)
        
        pdf.cell(200, 8, txt=f"Risk Level: {data['risk']}", ln=1)
        pdf.cell(200, 8, txt=f"Status: {data['status']}", ln=1)
        pdf.cell(200, 8, txt=f"Risk Score: {data.get('risk_score', 0)}%", ln=1)
        pdf.ln(5)
        
        # Recommendations
        pdf.set_font("Arial", "B", 12)
        pdf.cell(200, 10, txt="RECOMMENDATIONS", ln=1)
        pdf.set_font("Arial", "", 11)
        
        for rec in data.get("recommendations", [])[:5]:
            pdf.multi_cell(0, 8, txt=f"• {rec}")
        
        filename = f"aquaguard_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf.output(filename)
        return filename
    except Exception as e:
        st.error(f"PDF generation failed: {str(e)}")
        return None


st.set_page_config(page_title="AquaGuard AI", layout="wide", initial_sidebar_state="collapsed")

# =========================================================================
# PREMIUM PROFESSIONAL CSS
# =========================================================================
st.markdown("""
<style>
    /* Base styles */
    * {
        transition: all 0.2s ease;
    }
    
    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, #0a1628 0%, #1a2a4a 50%, #0d1f3c 100%);
        background-attachment: fixed;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Main container padding */
    .main .block-container {
        padding-top: 0rem !important;
        padding-bottom: 1rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
        max-width: 1400px;
    }
    
    /* Remove default streamlit top margin */
    .stApp header {
        display: none !important;
    }
    
    /* Professional glass card */
    .glass-card {
        background: rgba(20, 35, 60, 0.75);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.12);
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #00d4ff;
        display: inline-block;
        letter-spacing: -0.3px;
    }
    
    /* Card titles */
    .card-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    
    /* Metric values */
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        line-height: 1.2;
        color: #ffffff;
    }
    
    .metric-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #a0c4ff;
        margin-top: 0.25rem;
    }
    
    /* Risk level specific colors */
    .risk-safe { color: #00ff88; }
    .risk-moderate { color: #ffaa00; }
    .risk-high { color: #ff4444; }
    
    /* Crop recommendation box */
    .crop-recommendation {
        background: rgba(0, 212, 255, 0.1);
        backdrop-filter: blur(4px);
        border-radius: 12px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.6rem;
        border-left: 4px solid #00d4ff;
        font-size: 0.95rem;
        font-weight: 500;
        color: #ffffff;
    }
    
    /* Recommendation box */
    .rec-box {
        background: rgba(0, 212, 255, 0.08);
        backdrop-filter: blur(4px);
        border-radius: 12px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.6rem;
        font-size: 0.95rem;
        color: #ffffff;
        border-left: 3px solid #00d4ff;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(95deg, #00b4d8 0%, #00d4ff 100%);
        color: #ffffff;
        font-weight: 700;
        border: none;
        border-radius: 40px;
        padding: 0.6rem 1.2rem;
        font-size: 1rem;
        transition: all 0.2s;
        width: 100%;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,180,216,0.3);
        background: linear-gradient(95deg, #0096c7 0%, #00b4d8 100%);
    }
    
    /* Input labels */
    .stTextInput label, .stSelectbox label, .stSlider label, .stTextArea label {
        color: #a0c4ff !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        margin-bottom: 0.2rem;
    }
    
    /* Input fields */
    .stTextInput input, .stSelectbox select, .stTextArea textarea {
        background: rgba(10, 22, 40, 0.8) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(0, 212, 255, 0.3) !important;
        color: #ffffff !important;
        font-size: 0.9rem !important;
    }
    
    /* Slider styling */
    .stSlider .stSlider > div > div {
        background-color: #00d4ff;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: rgba(10, 22, 40, 0.5);
        border-radius: 60px;
        padding: 0.3rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 40px;
        padding: 0.4rem 1.2rem;
        font-weight: 600;
        color: #a0c4ff;
        font-size: 0.9rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(0, 212, 255, 0.25) !important;
        color: #ffffff !important;
    }
    
    /* Alert boxes */
    .stAlert {
        background: rgba(0, 212, 255, 0.1);
        backdrop-filter: blur(8px);
        border-radius: 16px;
        border-left: 4px solid #00d4ff;
        color: #ffffff;
    }
    
    /* Navigation top bar */
    .top-nav {
        background: rgba(10, 22, 40, 0.9);
        backdrop-filter: blur(12px);
        border-radius: 50px;
        padding: 0.6rem 1.5rem;
        margin-bottom: 1.5rem;
        margin-top: 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        border: 1px solid rgba(0, 212, 255, 0.2);
    }
    
    .logo-area {
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    
    .logo-icon {
        font-size: 1.8rem;
    }
    
    .logo-text {
        font-size: 1.3rem;
        font-weight: 700;
        color: #00d4ff;
        letter-spacing: -0.5px;
    }
    
    /* Footer */
    .custom-footer {
        text-align: center;
        padding: 1rem;
        color: #6c8db0;
        font-size: 0.75rem;
        margin-top: 1rem;
        border-top: 1px solid rgba(0, 212, 255, 0.1);
    }
    
    /* Welcome text */
    .welcome-text {
        font-size: 1rem;
        color: #c0d4f0;
        line-height: 1.5;
    }
    
    /* Login card */
    .login-card {
        background: rgba(10, 22, 40, 0.85);
        backdrop-filter: blur(20px);
        border-radius: 32px;
        padding: 2.5rem;
        margin-top: 0;
        box-shadow: 0 25px 50px rgba(0,0,0,0.3);
        border: 1px solid rgba(0, 212, 255, 0.3);
    }
    
    /* Metric card */
    .metric-card {
        background: rgba(0, 212, 255, 0.08);
        backdrop-filter: blur(8px);
        border-radius: 20px;
        padding: 1rem;
        text-align: center;
        height: 100%;
        border: 1px solid rgba(0, 212, 255, 0.15);
    }
    
    /* Crisis prediction box styles */
    .crisis-box {
        border-radius: 24px;
        padding: 1.8rem;
        margin: 0.5rem 0;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .crisis-box h3 {
        margin-bottom: 1rem;
        font-size: 1.4rem;
    }
    
    .crisis-box p {
        margin: 0.8rem 0;
        font-size: 1rem;
    }
    
    .crisis-safe {
        background: linear-gradient(135deg, rgba(46, 204, 113, 0.25), rgba(46, 204, 113, 0.1));
        border-left: 8px solid #2ecc71;
        border-right: 1px solid rgba(46, 204, 113, 0.3);
    }
    
    .crisis-moderate {
        background: linear-gradient(135deg, rgba(241, 196, 15, 0.25), rgba(241, 196, 15, 0.1));
        border-left: 8px solid #f1c40f;
        border-right: 1px solid rgba(241, 196, 15, 0.3);
    }
    
    .crisis-high {
        background: linear-gradient(135deg, rgba(231, 76, 60, 0.25), rgba(231, 76, 60, 0.1));
        border-left: 8px solid #e74c3c;
        border-right: 1px solid rgba(231, 76, 60, 0.3);
    }
    
    .crisis-severe {
        background: linear-gradient(135deg, rgba(192, 57, 43, 0.35), rgba(192, 57, 43, 0.15));
        border-left: 8px solid #c0392b;
        border-right: 1px solid rgba(192, 57, 43, 0.4);
    }
    
    /* All text colors */
    .stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, 
    .stMarkdown label, span, div, .stText {
        color: #e0e8f0 !important;
    }
    
    /* Headers specifically */
    h1, h2, h3, h4 {
        color: #ffffff !important;
    }
    
    /* Chart container */
    .chart-container {
        background: transparent;
        border-radius: 20px;
        padding: 0.5rem;
        margin-bottom: 0.8rem;
    }
    
    /* Plotly chart text visibility */
    .js-plotly-plot .main-svg {
        background: transparent !important;
    }
    
    /* Success/Warning/Error text */
    .stSuccess, .stWarning, .stError, .stInfo {
        color: #ffffff !important;
    }
    
    /* Info box */
    .stInfo {
        background: rgba(0, 180, 216, 0.15);
        backdrop-filter: blur(8px);
        border-radius: 16px;
    }
    
    /* Selectbox options */
    .stSelectbox div[data-baseweb="select"] div {
        background: rgba(10, 22, 40, 0.9);
    }
    
    /* Column equal height fix */
    div[data-testid="column"] {
        display: flex;
        flex-direction: column;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================================
# Session State
# =========================================================================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "pref_region" not in st.session_state:
    st.session_state["pref_region"] = "Kolar"
if "pred_results" not in st.session_state:
    st.session_state["pred_results"] = None
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "🏠 Dashboard"
if "last_prediction" not in st.session_state:
    st.session_state["last_prediction"] = None
if "chat_question" not in st.session_state:
    st.session_state["chat_question"] = ""

# Mock user database for demo
if "users" not in st.session_state:
    st.session_state["users"] = {}

# =========================================================================
# Data Lists
# =========================================================================
REGIONS_LIST = ["Kolar", "Tumkur", "Chitradurga", "Ballari", "Hubli", "Bengaluru", "Mysuru", "Belagavi", "Mumbai", "Delhi", "Chennai", "Kolkata", "Hyderabad", "Pune", "Ahmedabad", "Jaipur"]
CROPS_LIST = ["Rice", "Wheat", "Sugarcane", "Cotton", "Millets", "Maize", "Barley", "Soybeans", "Groundnut", "Sunflower", "Potato", "Tomato", "Onion", "Garlic"]
SEASONS_LIST = ["Winter", "Summer", "Monsoon", "Post_Monsoon"]

# =========================================================================
# Helper Functions
# =========================================================================
def get_crop_recommendation(temp, rainfall, borewell):
    recommendations = []
    
    if temp > 35:
        recommendations.append("🌾 **Millets** (Jowar, Bajra, Ragi) - Heat tolerant, low water")
        recommendations.append("🌿 **Sorghum** - Survives high temperatures")
        recommendations.append("🥜 **Groundnut** - Good for hot conditions")
    elif temp > 30:
        recommendations.append("🌽 **Maize** - Moderate heat tolerance")
        recommendations.append("🌻 **Sunflower** - Thrives in warm weather")
        recommendations.append("🫘 **Pulses** - Heat resistant")
    elif temp > 20:
        recommendations.append("🌾 **Wheat** - Ideal temperature range")
        recommendations.append("🌱 **Soybeans** - Good for moderate climate")
    else:
        recommendations.append("🌾 **Barley** - Cold tolerant")
        recommendations.append("🧄 **Garlic** - Grows well in cool weather")
    
    if rainfall < 50:
        recommendations.append("💧 **Drought-resistant varieties** recommended")
    elif rainfall < 100:
        recommendations.append("💦 **Improved irrigation** recommended")
    
    if borewell > 70:
        recommendations.append("⚠️ **Switch to drought-tolerant crops**")
        recommendations.append("🚰 **Implement drip irrigation**")
    
    return recommendations[:5]

def get_district_crisis_prediction(region, temp, rainfall, borewell):
    risk_score = 0
    
    if temp > 35:
        risk_score += 35
    elif temp > 32:
        risk_score += 25
    elif temp > 28:
        risk_score += 15
    
    if rainfall < 50:
        risk_score += 35
    elif rainfall < 100:
        risk_score += 25
    elif rainfall < 150:
        risk_score += 15
    
    if borewell > 80:
        risk_score += 30
    elif borewell > 60:
        risk_score += 20
    
    if risk_score >= 80:
        crisis_level = "SEVERE CRISIS"
        crisis_emoji = "🔴"
        crisis_color = "severe"
        years = "1-2 years"
        message = "⚠️ IMMEDIATE ACTION REQUIRED! Critical water shortage expected."
    elif risk_score >= 60:
        crisis_level = "HIGH RISK"
        crisis_emoji = "🟠"
        crisis_color = "high"
        years = "2-3 years"
        message = "⚠️ URGENT: High probability of water crisis. Take action now!"
    elif risk_score >= 40:
        crisis_level = "MODERATE RISK"
        crisis_emoji = "🟡"
        crisis_color = "moderate"
        years = "3-4 years"
        message = "⚠️ Watchful: Start water conservation measures now."
    elif risk_score >= 20:
        crisis_level = "LOW RISK"
        crisis_emoji = "🟢"
        crisis_color = "safe"
        years = "4-5 years"
        message = "ℹ️ Monitor: Current conditions are relatively stable."
    else:
        crisis_level = "STABLE"
        crisis_emoji = "✅"
        crisis_color = "safe"
        years = "5+ years"
        message = "✅ Good: Current practices are sustainable."
    
    return {
        "crisis_level": crisis_level,
        "crisis_emoji": crisis_emoji,
        "crisis_color": crisis_color,
        "timeframe": years,
        "risk_score": risk_score,
        "message": message,
        "recommendations": [
            "🌧️ Build rainwater harvesting structures",
            "💧 Switch to drip irrigation",
            "🌾 Plant drought-resistant varieties",
            "📊 Monitor groundwater monthly",
            "🤝 Join farmer water groups"
        ]
    }

def get_ai_response(question):
    q = question.lower()
    
    if any(word in q for word in ["rain", "water", "irrigation", "save"]):
        return """💧 **Water Management Tips:**

🌅 **Best Time to Water:** Early morning (6-8 AM) or evening (5-7 PM) - reduces evaporation by 30%

💦 **Efficient Methods:**
• Drip irrigation - saves 50-70% water
• Sprinkler system - saves 30-40% water

🌾 **Mulching:** Cover soil with straw - reduces evaporation by 70%

🌧️ **Rainwater Harvesting:** Collect every drop from your roof"""

    elif any(word in q for word in ["crop", "grow", "plant"]):
        return """🌾 **Crop Selection Guide:**

☀️ **For Hot & Dry Areas (>35°C):**
• Millets (Jowar, Bajra, Ragi)
• Sorghum, Groundnut

🌤️ **For Moderate Climate (25-35°C):**
• Maize, Cotton, Pulses, Wheat (winter)

🌧️ **For Good Water Availability:**
• Rice, Sugarcane, Vegetables

🔄 **Pro Tip:** Rotate crops to maintain soil health!"""

    elif any(word in q for word in ["pest", "insect", "bug"]):
        return """🐛 **Natural Pest Control:**

🌿 **Organic Solutions:**
• Neem oil spray - effective against 200+ pests
• Garlic-chili spray - homemade and safe

🦋 **Prevention:**
• Crop rotation breaks pest cycles
• Plant marigolds as natural repellents

⚠️ Use chemical pesticides only as last resort!"""

    elif any(word in q for word in ["fertilizer", "manure", "soil"]):
        return """🌱 **Soil Health Guide:**

💚 **Organic Fertilizers:**
• Compost - improves soil structure
• Farmyard manure - adds nutrients
• Vermicompost - rich in micronutrients

📊 **Application Tips:**
• Get soil tested every 6 months
• Apply early morning or evening
• Don't over-fertilize - wastes money"""

    else:
        return """🤖 **I'm your farming assistant!**

Ask me about:
• 💧 Water management - How to save water
• 🌾 Crop selection - Best crops for your area
• 🐛 Pest control - Natural pest management
• 🌱 Fertilizers - Soil health tips
• ⛲ Borewell - Groundwater management

Just type your farming question above!"""

def run_prediction(region, season, crop, rainfall, temp, borewell):
    risk_score = 0
    
    if rainfall < 100:
        risk_score += 30
    elif rainfall < 200:
        risk_score += 15
    
    if borewell > 80:
        risk_score += 35
    elif borewell > 60:
        risk_score += 25
    elif borewell > 40:
        risk_score += 15
    
    if crop in ["Rice", "Sugarcane"]:
        risk_score += 25
    
    if temp > 38:
        risk_score += 25
    elif temp > 35:
        risk_score += 20
    elif temp > 32:
        risk_score += 10
    
    if risk_score >= 65:
        risk = "High"
        status = "Critical - Immediate action required"
    elif risk_score >= 35:
        risk = "Moderate"
        status = "Watch - Monitor closely"
    else:
        risk = "Safe"
        status = "Normal - Continue current practices"
    
    if risk == "High":
        recommendations = [
            "🚨 IMMEDIATE: Stop all non-essential water usage",
            "💧 Switch to drip irrigation (saves 50% water)",
            "🌾 Plant drought-resistant millets or sorghum",
            "📊 Monitor groundwater levels daily",
            "🌧️ Implement rainwater harvesting urgently"
        ]
    elif risk == "Moderate":
        recommendations = [
            "⚠️ Reduce irrigation by 25-30%",
            "💧 Install soil moisture sensors",
            "🔄 Rotate with less water-intensive crops",
            "📈 Apply mulching to retain moisture",
            "💦 Irrigate during early morning or evening"
        ]
    else:
        recommendations = [
            "✅ Continue current irrigation practices",
            "💧 Maintain regular water level monitoring",
            "🌧️ Expand rainwater harvesting capacity",
            "📊 Keep water usage records",
            "🌱 Good time for water-intensive crops"
        ]
    
    groundwater = {
        "1_month": round(35 + (borewell / 100) * 20 + random.uniform(-5, 5), 1),
        "3_months": round(40 + (borewell / 100) * 25 + random.uniform(-8, 8), 1),
        "1_year": round(45 + (borewell / 100) * 30 + random.uniform(-10, 10), 1)
    }
    
    rainfall_forecast = {
        "1_month": max(0, round(rainfall * 0.9 + random.uniform(-10, 10), 1)),
        "3_months": max(0, round(rainfall * 0.75 + random.uniform(-20, 20), 1)),
        "1_year": max(0, round(rainfall * 0.6 + random.uniform(-30, 30), 1))
    }
    
    temperature_forecast = {
        "1_month": round(temp + random.uniform(-1, 2), 1),
        "3_months": round(temp + random.uniform(1, 4), 1),
        "1_year": round(temp + random.uniform(2, 5), 1)
    }
    
    return {
        "payload": {
            "region": region, "season": season, "crop_type": crop,
            "rainfall_mm": rainfall, "temperature_c": temp, "borewell_dependency": borewell
        },
        "risk": risk, "risk_score": risk_score, "status": status,
        "recommendations": recommendations,
        "forecasts": {"groundwater": groundwater, "rainfall": rainfall_forecast, "temperature": temperature_forecast},
        "crop_recommendations": get_crop_recommendation(temp, rainfall, borewell)
    }

# =========================================================================
# Top Navigation
# =========================================================================
def render_top_nav():
    st.markdown(f'''
        <div class="top-nav">
            <div class="logo-area">
                <span class="logo-icon">🌊💧</span>
                <span class="logo-text">AquaGuard AI</span>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    pages = ["🏠 Dashboard", "🤖 AI Assistant", "⚠️ Crisis Forecast"]
    cols = st.columns(len(pages))
    for i, page in enumerate(pages):
        with cols[i]:
            if st.button(page, key=f"nav_{page}", use_container_width=True):
                st.session_state["current_page"] = page
                st.rerun()

# =========================================================================
# LOGIN PAGE
# =========================================================================
def render_login():
    col1, col2, col3 = st.columns([1, 2.5, 1])
    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        
        st.markdown("""
            <div style="text-align:center;">
                <span style="font-size:4rem; display:inline-block; animation: wave 2s ease-in-out infinite;">🌊</span>
                <span style="font-size:3rem; margin-left:-10px;">💧</span>
            </div>
            <style>
                @keyframes wave {
                    0%, 100% { transform: translateY(0px); }
                    50% { transform: translateY(-10px); }
                }
            </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<h1 style="text-align:center; color:#00d4ff; margin-bottom:0.2rem;">AquaGuard AI</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center; color:#a0c4ff; margin-bottom:1.5rem;">Intelligent Groundwater Management System</p>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Secure Login", "📝 Create Account"])
        
        with tab1:
            st.markdown('<p style="color:#c0d4f0; font-size:0.9rem;">Welcome back! Please login to access your dashboard.</p>', unsafe_allow_html=True)
            username = st.text_input("Username", placeholder="Enter your username", key="login_user")
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pass")
            
            if st.button("Access Dashboard →", use_container_width=True):
                if username and password:
                    if username in st.session_state["users"] and st.session_state["users"][username] == password:
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = username
                        st.rerun()
                    elif username == "demo" and password == "demo":
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = "Farmer"
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials. Try 'demo' / 'demo'")
                else:
                    st.warning("⚠️ Please enter both username and password")
        
        with tab2:
            st.markdown('<p style="color:#c0d4f0; font-size:0.9rem;">Join AquaGuard AI to start smart water management.</p>', unsafe_allow_html=True)
            new_user = st.text_input("Username", placeholder="Choose a username", key="signup_user")
            new_email = st.text_input("Email", placeholder="Enter your email", key="signup_email")
            new_pass = st.text_input("Password", type="password", placeholder="Choose a password", key="signup_pass")
            confirm_pass = st.text_input("Confirm Password", type="password", placeholder="Confirm your password", key="signup_confirm")
            
            if st.button("Create Free Account →", use_container_width=True):
                if new_user and new_pass and new_email:
                    if new_pass == confirm_pass:
                        if new_user not in st.session_state["users"]:
                            st.session_state["users"][new_user] = new_pass
                            st.success("✅ Account created! Please login.")
                        else:
                            st.error("❌ Username already exists")
                    else:
                        st.error("❌ Passwords do not match")
                else:
                    st.warning("⚠️ Please fill all fields")
        
        st.markdown("---")
        st.markdown('<p style="text-align:center; color:#6c8db0; font-size:0.8rem;">🔐 Demo Access: username: <strong style="color:#00d4ff;">demo</strong> | password: <strong style="color:#00d4ff;">demo</strong></p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================================
# DASHBOARD - Correct Order: Results → Explanation → Crops → Graphs → Recommendations
# =========================================================================
def render_dashboard():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("<div class='card-title'>🔮 Smart Farm Analysis</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        region = st.selectbox("📍 Select Region", REGIONS_LIST, 
                              index=REGIONS_LIST.index(st.session_state["pref_region"]) if st.session_state["pref_region"] in REGIONS_LIST else 0)
        season = st.selectbox("🌱 Season", SEASONS_LIST)
        crop = st.selectbox("🌾 Crop Type", CROPS_LIST)
    
    with col2:
        rainfall = st.slider("💧 Rainfall (mm per year)", 0, 500, 120)
        temperature = st.slider("🌡️ Temperature (°C)", 10.0, 50.0, 28.0)
        borewell = st.slider("⛲ Borewell Dependency (%)", 0, 100, 60)
    
    if st.button("🔍 Analyze & Predict", use_container_width=True):
        with st.spinner("🌾 Analyzing farm data..."):
            results = run_prediction(region, season, crop, rainfall, temperature, borewell)
            st.session_state["pred_results"] = results
            st.session_state["last_prediction"] = results
            st.success("✅ Analysis complete!")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.get("pred_results"):
        results = st.session_state["pred_results"]
        
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("<div class='section-header'>📊 Analysis Results</div>", unsafe_allow_html=True)
        
        # Row 1: Four equal metric cards
        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            risk_class = "risk-safe" if results['risk'] == "Safe" else "risk-moderate" if results['risk'] == "Moderate" else "risk-high"
            st.markdown(f'''
                <div class="metric-card" style="min-height:120px;">
                    <div class="metric-label">💧 Water Risk Level</div>
                    <div class="metric-value {risk_class}" style="font-size:1.8rem;">{results['risk']}</div>
                    <div class="metric-label">Score: {results['risk_score']}%</div>
                </div>
            ''', unsafe_allow_html=True)
        with col_b:
            st.markdown(f'''
                <div class="metric-card" style="min-height:120px;">
                    <div class="metric-label">📋 Status</div>
                    <div class="metric-value" style="font-size:1rem; margin-top:10px;">{results['status'][:35]}</div>
                </div>
            ''', unsafe_allow_html=True)
        with col_c:
            gw = results['forecasts']['groundwater']['1_month']
            st.markdown(f'''
                <div class="metric-card" style="min-height:120px;">
                    <div class="metric-label">💧 Water Level</div>
                    <div class="metric-value" style="font-size:2rem;">{gw}<span style="font-size:1rem;"> m</span></div>
                    <div class="metric-label">Below ground level</div>
                </div>
            ''', unsafe_allow_html=True)
        with col_d:
            st.markdown(f'''
                <div class="metric-card" style="min-height:120px;">
                    <div class="metric-label">🌡️ Current Temp</div>
                    <div class="metric-value" style="font-size:2rem;">{results['payload']['temperature_c']}<span style="font-size:1rem;">°C</span></div>
                </div>
            ''', unsafe_allow_html=True)
        
        # =============================================================
        # 1. ANALYSIS EXPLANATION (After Results)
        # =============================================================
        st.markdown("<div class='section-header' style='margin-top:20px;'>📋 Analysis Explanation</div>", unsafe_allow_html=True)
        if results['risk'] == "Safe":
            st.success(f"✅ **Good News!** Your farm is in a good position. Based on your inputs: Rainfall={results['payload']['rainfall_mm']}mm, Temperature={results['payload']['temperature_c']}°C, Borewell={results['payload']['borewell_dependency']}% - the water risk level is **{results['risk']}**.")
        elif results['risk'] == "Moderate":
            st.warning(f"⚠️ **Attention Needed.** Your farm shows moderate water stress. Based on your inputs: Rainfall={results['payload']['rainfall_mm']}mm, Temperature={results['payload']['temperature_c']}°C, Borewell={results['payload']['borewell_dependency']}% - the water risk level is **{results['risk']}**.")
        else:
            st.error(f"🔴 **Critical Alert!** Your farm is at high risk of water shortage. Based on your inputs: Rainfall={results['payload']['rainfall_mm']}mm, Temperature={results['payload']['temperature_c']}°C, Borewell={results['payload']['borewell_dependency']}% - the water risk level is **{results['risk']}**.")
        
        # =============================================================
        # 2. RECOMMENDED CROPS
        # =============================================================
        st.markdown("<div class='section-header' style='margin-top:20px;'>🌾 Recommended Crops</div>", unsafe_allow_html=True)
        rec_cols = st.columns(2)
        for idx, rec in enumerate(results['crop_recommendations']):
            with rec_cols[idx % 2]:
                st.markdown(f'<div class="crop-recommendation">{rec}</div>', unsafe_allow_html=True)
        
        # =============================================================
        # 3. VISUAL ANALYSIS (Graphs)
        # =============================================================
        st.markdown("<div class='section-header' style='margin-top:20px;'>📈 Visual Analysis</div>", unsafe_allow_html=True)
        
        # Row 1: Graph 1 (Bar) and Graph 2 (Line)
        col_ch1, col_ch2 = st.columns(2)
        
        with col_ch1:
            st.markdown("**💧 Rainfall Forecast (Bar Graph)**")
            rf = results['forecasts']['rainfall']
            
            fig_bar_rainfall = go.Figure()
            fig_bar_rainfall.add_trace(go.Bar(
                x=['1 Month', '3 Months', '1 Year'],
                y=[rf['1_month'], rf['3_months'], rf['1_year']],
                name='Rainfall',
                marker_color=['#00b4d8', '#0096c7', '#0077b6'],
                text=[f"{rf['1_month']} mm", f"{rf['3_months']} mm", f"{rf['1_year']} mm"],
                textposition='outside',
                textfont=dict(size=12, color='white'),
                width=0.6
            ))
            fig_bar_rainfall.update_layout(
                plot_bgcolor='rgba(0,0,0,0.2)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#ffffff', size=12),
                height=400,
                xaxis_title="Time Period",
                yaxis_title="Rainfall (mm)",
                margin=dict(l=50, r=50, t=50, b=50),
                showlegend=False
            )
            fig_bar_rainfall.update_xaxes(
                gridcolor='rgba(255,255,255,0.15)',
                title_font=dict(color='#ffffff', size=12),
                tickfont=dict(color='#ffffff', size=11)
            )
            fig_bar_rainfall.update_yaxes(
                gridcolor='rgba(255,255,255,0.15)',
                title_font=dict(color='#ffffff', size=12),
                tickfont=dict(color='#ffffff', size=11)
            )
            st.plotly_chart(fig_bar_rainfall, use_container_width=True, config={'displayModeBar': False})
        
        with col_ch2:
            st.markdown("**🌡️ Temperature Trend (Line Graph)**")
            tmp = results['forecasts']['temperature']
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=['1 Month', '3 Months', '1 Year'],
                y=[tmp['1_month'], tmp['3_months'], tmp['1_year']],
                mode='lines+markers',
                name='Temperature',
                line=dict(color='#ff6b35', width=4, shape='spline'),
                marker=dict(size=14, color='#ff8c42', symbol='diamond', line=dict(width=2, color='white'))
            ))
            fig_line.update_layout(
                plot_bgcolor='rgba(0,0,0,0.2)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#ffffff', size=12),
                height=400,
                xaxis_title="Time Period",
                yaxis_title="Temperature (°C)",
                margin=dict(l=50, r=50, t=50, b=50)
            )
            fig_line.update_xaxes(
                gridcolor='rgba(255,255,255,0.15)',
                title_font=dict(color='#ffffff', size=12),
                tickfont=dict(color='#ffffff', size=11)
            )
            fig_line.update_yaxes(
                gridcolor='rgba(255,255,255,0.15)',
                title_font=dict(color='#ffffff', size=12),
                tickfont=dict(color='#ffffff', size=11)
            )
            st.plotly_chart(fig_line, use_container_width=True, config={'displayModeBar': False})
        
        # Row 2: Graph 3 (Bar + Scatter) and Graph 4 (Donut)
        col_ch3, col_ch4 = st.columns(2)
        
        with col_ch3:
            st.markdown("**💧 Groundwater Depth Analysis**")
            gw = results['forecasts']['groundwater']
            
            fig_bar_gw = go.Figure()
            fig_bar_gw.add_trace(go.Bar(
                x=['1 Month', '3 Months', '1 Year'],
                y=[gw['1_month'], gw['3_months'], gw['1_year']],
                name='Depth',
                marker_color=['#00d4ff', '#00b4d8', '#0096c7'],
                text=[f"{gw['1_month']}m", f"{gw['3_months']}m", f"{gw['1_year']}m"],
                textposition='outside',
                textfont=dict(size=12, color='white'),
                width=0.6
            ))
            fig_bar_gw.add_trace(go.Scatter(
                x=['1 Month', '3 Months', '1 Year'],
                y=[gw['1_month'], gw['3_months'], gw['1_year']],
                mode='lines+markers',
                name='Trend',
                line=dict(color='#ffd166', width=3, dash='dot'),
                marker=dict(size=12, color='#ffd166', symbol='circle')
            ))
            fig_bar_gw.update_layout(
                plot_bgcolor='rgba(0,0,0,0.2)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#ffffff', size=12),
                height=400,
                xaxis_title="Time Period",
                yaxis_title="Depth (meters)",
                margin=dict(l=50, r=50, t=50, b=50),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            fig_bar_gw.update_xaxes(
                gridcolor='rgba(255,255,255,0.15)',
                title_font=dict(color='#ffffff', size=12),
                tickfont=dict(color='#ffffff', size=11)
            )
            fig_bar_gw.update_yaxes(
                gridcolor='rgba(255,255,255,0.15)',
                title_font=dict(color='#ffffff', size=12),
                tickfont=dict(color='#ffffff', size=11)
            )
            st.plotly_chart(fig_bar_gw, use_container_width=True, config={'displayModeBar': False})
        
        with col_ch4:
            st.markdown("**🥧 Risk Distribution**")
            risk_dist = {
                'Water Scarcity': max(0, results['risk_score'] * 0.5),
                'Temperature Stress': max(0, results['risk_score'] * 0.3),
                'Crop Demand': max(0, results['risk_score'] * 0.2),
                'Normal': max(10, 100 - results['risk_score'])
            }
            fig_donut = go.Figure(data=[go.Pie(
                labels=list(risk_dist.keys()),
                values=list(risk_dist.values()),
                hole=0.5,
                marker=dict(colors=['#ff4444', '#ff8c42', '#00b4d8', '#2ecc71']),
                textinfo='percent+label',
                textposition='auto',
                textfont=dict(color='#ffffff', size=11),
                pull=[0.05, 0, 0, 0]
            )])
            fig_donut.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#ffffff', size=12),
                height=400,
                margin=dict(l=20, r=20, t=40, b=20),
                showlegend=True,
                legend=dict(orientation="v", yanchor="middle", x=1.1)
            )
            st.plotly_chart(fig_donut, use_container_width=True, config={'displayModeBar': False})
        
        # =============================================================
        # 4. EXPERT RECOMMENDATIONS (After Graphs)
        # =============================================================
        st.markdown("<div class='section-header' style='margin-top:20px;'>💡 Expert Recommendations</div>", unsafe_allow_html=True)
        for rec in results['recommendations']:
            st.markdown(f'<div class="rec-box">{rec}</div>', unsafe_allow_html=True)
        
        # PDF Download
        col_pdf1, col_pdf2, col_pdf3 = st.columns([1, 2, 1])
        with col_pdf2:
            if st.button("📥 Download PDF Report", use_container_width=True):
                with st.spinner("Generating PDF..."):
                    pdf_file = generate_pdf_report(results)
                    if pdf_file and os.path.exists(pdf_file):
                        with open(pdf_file, "rb") as f:
                            st.download_button("📄 Save PDF", f, file_name=pdf_file, mime="application/pdf", use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================================
# AI ASSISTANT PAGE
# =========================================================================
def render_chatbot():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("<div class='card-title' style='font-size:1.8rem;'>🤖 AI Farming Assistant</div>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="welcome-text" style="font-size:1.1rem;">
            Ask me anything about farming! I can help with water management, crop selection, pest control, and more.
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📌 Quick Questions:")
    q_cols = st.columns(3)
    quick_qs = ["How to save water?", "Best crops for dry areas?", "Pest control tips?"]
    
    for i, q in enumerate(quick_qs):
        with q_cols[i]:
            if st.button(f"💡 {q}", use_container_width=True):
                st.session_state["chat_question"] = q
    
    st.markdown("---")
    
    user_q = st.text_area("💬 Your Question:", value=st.session_state.get("chat_question", ""), 
                          placeholder="Example: What is the best time to water my crops?", height=100)
    
    if st.button("🔍 Get Answer", use_container_width=True):
        if user_q:
            with st.spinner("🤔 Thinking..."):
                response = get_ai_response(user_q)
                st.markdown(f'''
                    <div style="background:rgba(0,180,216,0.12); backdrop-filter:blur(8px); border-radius:20px; padding:1.5rem; margin-top:1rem; border-left:4px solid #00d4ff;">
                        <strong style="color:#00d4ff; font-size:1.2rem;">🤖 AI Assistant:</strong><br><br>
                        <div style="color:#ffffff; font-size:1rem; line-height:1.6;">{response}</div>
                    </div>
                ''', unsafe_allow_html=True)
        else:
            st.warning("⚠️ Please enter your question first.")
    
    st.markdown("---")
    st.markdown("### 📚 Helpful Farming Tips")
    
    tips = [
        "💧 Water early morning or evening - Reduces evaporation by 30%",
        "🌾 Grow local varieties - They need less care and water",
        "🧪 Test your soil every 6 months - Saves fertilizer money",
        "🌧️ Harvest rainwater - Every drop counts!",
        "🐞 Use neem oil for pests - Safe and effective"
    ]
    
    for tip in tips:
        st.markdown(f'<div class="rec-box" style="font-size:1rem;">{tip}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================================
# CRISIS FORECAST PAGE - FIXED UI
# =========================================================================
def render_crisis_forecast():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("<div class='card-title'>⚠️ District Crisis Forecast (3-5 Years)</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="welcome-text">
        This tool predicts which districts may face water crisis in the next 3-5 years based on current patterns.
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        district = st.selectbox("📍 Select District:", REGIONS_LIST)
        current_rainfall = st.slider("💧 Annual Rainfall (mm):", 0, 500, 120)
    
    with col2:
        avg_temperature = st.slider("🌡️ Average Temperature (°C):", 20.0, 45.0, 30.0)
        borewell_density = st.slider("⛲ Borewell Dependency (%):", 0, 100, 65)
    
    if st.button("🔮 Predict District Crisis", use_container_width=True):
        with st.spinner("Analyzing 5-year forecast..."):
            crisis = get_district_crisis_prediction(district, avg_temperature, current_rainfall, borewell_density)
            
            st.markdown(f'''
                <div style="background:rgba(0,131,143,0.15); backdrop-filter:blur(8px); border-radius:24px; padding:1.5rem; margin-top:1.5rem;">
                    <h3 style="color:#000000; margin-bottom:0.5rem;">📊 {district} - 5 Year Forecast</h3>
                    <hr style="margin:0.5rem 0;">
                    <p><strong>Crisis Level:</strong> {crisis["crisis_level"]}</p>
                    <p><strong>Timeframe:</strong> {crisis["timeframe"]}</p>
                    <p><strong>Risk Score:</strong> {crisis["risk_score"]}/100</p>
                    <p><strong>Analysis:</strong> {crisis["message"]}</p>
                </div>
            ''', unsafe_allow_html=True)
            
            st.markdown("<div class='section-header' style='margin-top:25px;'>💡 Recommendations</div>", unsafe_allow_html=True)
            for rec in crisis["recommendations"]:
                st.markdown(f'<div class="rec-box">{rec}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.info("ℹ️ This forecast considers temperature trends, rainfall patterns, and borewell dependency to predict future water availability.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================================
# MAIN
# =========================================================================
def main():
    if not st.session_state.get("logged_in", False):
        render_login()
    else:
        render_top_nav()
        current_page = st.session_state.get("current_page", "🏠 Dashboard")
        
        if current_page == "🏠 Dashboard":
            render_dashboard()
        elif current_page == "🤖 AI Assistant":
            render_chatbot()
        elif current_page == "⚠️ Crisis Forecast":
            render_crisis_forecast()
        else:
            render_dashboard()
        
        st.markdown("""
            <div class="custom-footer">
                🌊 AquaGuard AI - Smart Water Management System | Real-time Analytics & Predictions
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()