import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from fpdf import FPDF
import os
from dotenv import load_dotenv
from streamlit_option_menu import option_menu
import datetime
import random


# Add this function after imports
def generate_pdf_report(data, lang):
    """Generate PDF report in selected language"""
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", "B", 16)
    title = "AquaGuard AI - Water Management Report" if lang == "English" else "एक्वागार्ड एआई - जल प्रबंधन रिपोर्ट" if lang == "Hindi" else "ಅಕ್ವಾಗಾರ್ಡ್ ಎಐ - ಜಲ ನಿರ್ವಹಣಾ ವರದಿ"
    pdf.cell(200, 10, txt=title, ln=1, align='C')
    pdf.ln(10)
    
    # Date
    pdf.set_font("Arial", "", 10)
    date_text = f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    pdf.cell(200, 10, txt=date_text, ln=1, align='R')
    pdf.ln(5)
    
    # Input Parameters
    pdf.set_font("Arial", "B", 12)
    input_title = "INPUT PARAMETERS" if lang == "English" else "इनपुट पैरामीटर" if lang == "Hindi" else "ಇನ್ಪುಟ್ ನಿಯತಾಂಕಗಳು"
    pdf.cell(200, 10, txt=input_title, ln=1)
    pdf.set_font("Arial", "", 11)
    
    region_label = "Region:" if lang == "English" else "क्षेत्र:" if lang == "Hindi" else "ಪ್ರದೇಶ:"
    crop_label = "Crop:" if lang == "English" else "फसल:" if lang == "Hindi" else "ಬೆಳೆ:"
    season_label = "Season:" if lang == "English" else "मौसम:" if lang == "Hindi" else "ಋತು:"
    
    pdf.cell(200, 8, txt=f"{region_label} {data['payload']['region']}", ln=1)
    pdf.cell(200, 8, txt=f"{crop_label} {data['payload']['crop_type']}", ln=1)
    pdf.cell(200, 8, txt=f"{season_label} {data['payload']['season']}", ln=1)
    pdf.cell(200, 8, txt=f"Rainfall: {data['payload']['rainfall_mm']} mm", ln=1)
    pdf.cell(200, 8, txt=f"Temperature: {data['payload']['temperature_c']}°C", ln=1)
    pdf.cell(200, 8, txt=f"Borewell Dependency: {data['payload']['borewell_dependency']}%", ln=1)
    pdf.ln(5)
    
    # Results
    pdf.set_font("Arial", "B", 12)
    results_title = "ANALYSIS RESULTS" if lang == "English" else "विश्लेषण परिणाम" if lang == "Hindi" else "ವಿಶ್ಲೇಷಣಾ ಫಲಿತಾಂಶಗಳು"
    pdf.cell(200, 10, txt=results_title, ln=1)
    pdf.set_font("Arial", "", 11)
    
    risk_label = "Risk Level:" if lang == "English" else "जोखिम स्तर:" if lang == "Hindi" else "ಅಪಾಯದ ಮಟ್ಟ:"
    status_label = "Status:" if lang == "English" else "स्थिति:" if lang == "Hindi" else "ಸ್ಥಿತಿ:"
    score_label = "Risk Score:" if lang == "English" else "जोखिम स्कोर:" if lang == "Hindi" else "ಅಪಾಯ ಸ್ಕೋರ್:"
    
    pdf.cell(200, 8, txt=f"{risk_label} {data['risk']}", ln=1)
    pdf.cell(200, 8, txt=f"{status_label} {data['status']}", ln=1)
    pdf.cell(200, 8, txt=f"{score_label} {data.get('risk_score', 0)}%", ln=1)
    pdf.ln(5)
    
    # Forecasts
    pdf.set_font("Arial", "B", 12)
    forecast_title = "FORECASTS" if lang == "English" else "पूर्वानुमान" if lang == "Hindi" else "ಮುನ್ಸೂಚನೆಗಳು"
    pdf.cell(200, 10, txt=forecast_title, ln=1)
    pdf.set_font("Arial", "", 11)
    
    gw = data['forecasts'].get('groundwater', {})
    pdf.cell(200, 8, txt=f"Groundwater Depth - 1 Month: {gw.get('1_month', 45)}m, 3 Months: {gw.get('3_months', 52)}m, 1 Year: {gw.get('1_year', 60)}m", ln=1)
    
    rf = data['forecasts'].get('rainfall', {})
    pdf.cell(200, 8, txt=f"Rainfall - 1 Month: {rf.get('1_month', 85)}mm, 3 Months: {rf.get('3_months', 72)}mm, 1 Year: {rf.get('1_year', 58)}mm", ln=1)
    
    tmp = data['forecasts'].get('temperature', {})
    pdf.cell(200, 8, txt=f"Temperature - 1 Month: {tmp.get('1_month', 28)}°C, 3 Months: {tmp.get('3_months', 31)}°C, 1 Year: {tmp.get('1_year', 33)}°C", ln=1)
    pdf.ln(5)
    
    # Recommendations
    pdf.set_font("Arial", "B", 12)
    rec_title = "RECOMMENDATIONS" if lang == "English" else "सुझाव" if lang == "Hindi" else "ಸಲಹೆಗಳು"
    pdf.cell(200, 10, txt=rec_title, ln=1)
    pdf.set_font("Arial", "", 11)
    
    for rec in data["recommendations"]:
        pdf.multi_cell(0, 8, txt=f"• {rec}")
    
    # Save PDF
    filename = f"aquaguard_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)
    return filename

load_dotenv(override=True)

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
API_KEY = os.getenv("API_KEY", "default-insecure-key")

st.set_page_config(page_title="AquaGuard AI", layout="wide", initial_sidebar_state="expanded")

# ORIGINAL DARK THEME CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800&family=Inter:wght@400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
    }
    
    .typing-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { text-shadow: 0px 0px 10px rgba(0, 242, 254, 0.4); }
        to { text-shadow: 0px 0px 30px rgba(0, 242, 254, 0.8); }
    }
    
    .subtitle {
        text-align: center;
        color: #00f2fe;
        font-size: 1rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 1.5rem;
    }
    
    .glass-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.2rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: transform 0.3s;
    }
    
    .glass-container:hover {
        transform: translateY(-3px);
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        color: white;
        border: none;
        border-radius: 8px;
        transition: all 0.3s;
        font-weight: bold;
        padding: 10px;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 20px rgba(0, 242, 254, 0.5);
    }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(0, 242, 254, 0.1), rgba(79, 172, 254, 0.1));
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        border: 1px solid rgba(0, 242, 254, 0.3);
    }
    
    .risk-safe { color: #10B981; font-weight: bold; font-size: 24px; }
    .risk-moderate { color: #F59E0B; font-weight: bold; font-size: 24px; }
    .risk-high { color: #EF4444; font-weight: bold; font-size: 24px; }
    
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stSelectbox label, .stSlider label {
        color: white !important;
    }
    
    .stTextInput label {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Session State
if "token" not in st.session_state:
    st.session_state["token"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None
if "pref_region" not in st.session_state:
    st.session_state["pref_region"] = "Kolar"
if "pred_results" not in st.session_state:
    st.session_state["pred_results"] = None
if "lang" not in st.session_state:
    st.session_state["lang"] = "English"

HEADERS = {"X-API-Key": st.session_state.get("token", API_KEY)}

# =========================================================================
# COMPLETE TRANSLATIONS FOR ALL LANGUAGES
# =========================================================================

# Region translations
REGION_TRANSLATIONS = {
    "English": {
        "Kolar": "Kolar", "Tumkur": "Tumkur", "Chitradurga": "Chitradurga", 
        "Ballari": "Ballari", "Hubli": "Hubli", "Bengaluru": "Bengaluru", 
        "Mysuru": "Mysuru", "Belagavi": "Belagavi", "Mumbai": "Mumbai", 
        "Delhi": "Delhi", "Chennai": "Chennai", "Kolkata": "Kolkata", 
        "Hyderabad": "Hyderabad", "Pune": "Pune", "Ahmedabad": "Ahmedabad", 
        "Jaipur": "Jaipur"
    },
    "Hindi": {
        "Kolar": "कोलार", "Tumkur": "तुमकुर", "Chitradurga": "चित्रदुर्ग", 
        "Ballari": "बल्लारी", "Hubli": "हुबली", "Bengaluru": "बेंगलुरु", 
        "Mysuru": "मैसूर", "Belagavi": "बेलगावी", "Mumbai": "मुंबई", 
        "Delhi": "दिल्ली", "Chennai": "चेन्नई", "Kolkata": "कोलकाता", 
        "Hyderabad": "हैदराबाद", "Pune": "पुणे", "Ahmedabad": "अहमदाबाद", 
        "Jaipur": "जयपुर"
    },
    "Kannada": {
        "Kolar": "ಕೋಲಾರ", "Tumkur": "ತುಮಕೂರು", "Chitradurga": "ಚಿತ್ರದುರ್ಗ", 
        "Ballari": "ಬಳ್ಳಾರಿ", "Hubli": "ಹುಬ್ಬಳ್ಳಿ", "Bengaluru": "ಬೆಂಗಳೂರು", 
        "Mysuru": "ಮೈಸೂರು", "Belagavi": "ಬೆಳಗಾವಿ", "Mumbai": "ಮುಂಬೈ", 
        "Delhi": "ದೆಹಲಿ", "Chennai": "ಚೆನ್ನೈ", "Kolkata": "ಕೋಲ್ಕತ್ತಾ", 
        "Hyderabad": "ಹೈದರಾಬಾದ್", "Pune": "ಪುಣೆ", "Ahmedabad": "ಅಹಮದಾಬಾದ್", 
        "Jaipur": "ಜೈಪುರ್"
    },
    "Telugu": {
        "Kolar": "కోలార్", "Tumkur": "తుమకూరు", "Chitradurga": "చిత్రదుర్గ", 
        "Ballari": "బళ్ళారి", "Hubli": "హుబ్లీ", "Bengaluru": "బెంగళూరు", 
        "Mysuru": "మైసూర్", "Belagavi": "బెలగావి", "Mumbai": "ముంబై", 
        "Delhi": "ఢిల్లీ", "Chennai": "చెన్నై", "Kolkata": "కోల్కతా", 
        "Hyderabad": "హైదరాబాద్", "Pune": "పూణే", "Ahmedabad": "అహ్మదాబాద్", 
        "Jaipur": "జైపూర్"
    },
    "Tamil": {
        "Kolar": "கோலார்", "Tumkur": "தும்கூர்", "Chitradurga": "சித்ரதுர்கா", 
        "Ballari": "பள்ளாரி", "Hubli": "ஹூப்ளி", "Bengaluru": "பெங்களூரு", 
        "Mysuru": "மைசூர்", "Belagavi": "பெலகாவி", "Mumbai": "மும்பை", 
        "Delhi": "டெல்லி", "Chennai": "சென்னை", "Kolkata": "கொல்கத்தா", 
        "Hyderabad": "ஹைதராபாத்", "Pune": "புனே", "Ahmedabad": "அகமதாபாத்", 
        "Jaipur": "ஜெய்ப்பூர்"
    },
    "Marathi": {
        "Kolar": "कोलार", "Tumkur": "तुमकुर", "Chitradurga": "चित्रदुर्ग", 
        "Ballari": "बल्लारी", "Hubli": "हुबळी", "Bengaluru": "बेंगळुरू", 
        "Mysuru": "म्हैसूर", "Belagavi": "बेळगावी", "Mumbai": "मुंबई", 
        "Delhi": "दिल्ली", "Chennai": "चेन्नई", "Kolkata": "कोलकाता", 
        "Hyderabad": "हैदराबाद", "Pune": "पुणे", "Ahmedabad": "अहमदाबाद", 
        "Jaipur": "जयपूर"
    }
}

# Crop translations
CROP_TRANSLATIONS = {
    "English": {
        "Rice": "Rice", "Wheat": "Wheat", "Sugarcane": "Sugarcane", "Cotton": "Cotton",
        "Millets": "Millets", "Maize": "Maize", "Barley": "Barley", "Soybeans": "Soybeans",
        "Groundnut": "Groundnut", "Sunflower": "Sunflower", "Potato": "Potato", "Tomato": "Tomato",
        "Onion": "Onion", "Garlic": "Garlic"
    },
    "Hindi": {
        "Rice": "चावल", "Wheat": "गेहूं", "Sugarcane": "गन्ना", "Cotton": "कपास",
        "Millets": "बाजरा", "Maize": "मक्का", "Barley": "जौ", "Soybeans": "सोयाबीन",
        "Groundnut": "मूंगफली", "Sunflower": "सूरजमुखी", "Potato": "आलू", "Tomato": "टमाटर",
        "Onion": "प्याज", "Garlic": "लहसुन"
    },
    "Kannada": {
        "Rice": "ಭತ್ತ", "Wheat": "ಗೋಧಿ", "Sugarcane": "ಕಬ್ಬು", "Cotton": "ಹತ್ತಿ",
        "Millets": "ಸಿರಿಧಾನ್ಯ", "Maize": "ಮೆಕ್ಕೆಜೋಳ", "Barley": "ಬಾರ್ಲಿ", "Soybeans": "ಸೋಯಾಬೀನ್",
        "Groundnut": "ಕಡಲೆಕಾಯಿ", "Sunflower": "ಸೂರ್ಯಕಾಂತಿ", "Potato": "ಆಲೂಗಡ್ಡೆ", "Tomato": "ಟೊಮೇಟೊ",
        "Onion": "ಈರುಳ್ಳಿ", "Garlic": "ಬೆಳ್ಳುಳ್ಳಿ"
    },
    "Telugu": {
        "Rice": "వరి", "Wheat": "గోధుమ", "Sugarcane": "చెరకు", "Cotton": "పత్తి",
        "Millets": "మిల్లెట్స్", "Maize": "మొక్కజొన్న", "Barley": "బార్లీ", "Soybeans": "సోయాబీన్స్",
        "Groundnut": "వేరుశెనగ", "Sunflower": "పొద్దుతిరుగుడు", "Potato": "బంగాళదుంప", "Tomato": "టమాటో",
        "Onion": "ఉల్లిపాయ", "Garlic": "వెల్లుల్లి"
    },
    "Tamil": {
        "Rice": "அரிசி", "Wheat": "கோதுமை", "Sugarcane": "கரும்பு", "Cotton": "பருத்தி",
        "Millets": "சிறுதானியங்கள்", "Maize": "மக்காச்சோளம்", "Barley": "பார்லி", "Soybeans": "சோயாபீன்ஸ்",
        "Groundnut": "நிலக்கடலை", "Sunflower": "சூரியகாந்தி", "Potato": "உருளைக்கிழங்கு", "Tomato": "தக்காளி",
        "Onion": "வெங்காயம்", "Garlic": "பூண்டு"
    },
    "Marathi": {
        "Rice": "तांदूळ", "Wheat": "गहू", "Sugarcane": "उस", "Cotton": "कापूस",
        "Millets": "बाजरी", "Maize": "मका", "Barley": "जव", "Soybeans": "सोयाबीन",
        "Groundnut": "शेंगदाणा", "Sunflower": "सूर्यफूल", "Potato": "बटाटा", "Tomato": "टोमॅटो",
        "Onion": "कांदा", "Garlic": "लसूण"
    }
}

# Season translations
SEASON_TRANSLATIONS = {
    "English": {"Winter": "Winter", "Summer": "Summer", "Monsoon": "Monsoon", "Post_Monsoon": "Post-Monsoon"},
    "Hindi": {"Winter": "सर्दी", "Summer": "गर्मी", "Monsoon": "मानसून", "Post_Monsoon": "शरद ऋतु"},
    "Kannada": {"Winter": "ಚಳಿಗಾಲ", "Summer": "ಬೇಸಿಗೆ", "Monsoon": "ಮಾನ್ಸೂನ್", "Post_Monsoon": "ಶರತ್ಕಾಲ"},
    "Telugu": {"Winter": "శీతాకాలం", "Summer": "వేసవి", "Monsoon": "వర్షాకాలం", "Post_Monsoon": "శరదృతువు"},
    "Tamil": {"Winter": "குளிர்காலம்", "Summer": "கோடை", "Monsoon": "பருவமழை", "Post_Monsoon": "இலையுதிர் காலம்"},
    "Marathi": {"Winter": "हिवाळा", "Summer": "उन्हाळा", "Monsoon": "पावसाळा", "Post_Monsoon": "शरद ऋतू"}
}

# Status translations
STATUS_TRANSLATIONS = {
    "English": {"Safe": "Safe", "Moderate": "Moderate", "High": "High"},
    "Hindi": {"Safe": "सुरक्षित", "Moderate": "मध्यम", "High": "उच्च"},
    "Kannada": {"Safe": "ಸುರಕ್ಷಿತ", "Moderate": "ಮಧ್ಯಮ", "High": "ಉಚ್ಚ"},
    "Telugu": {"Safe": "సురక్షితం", "Moderate": "మితమైన", "High": "అధిక"},
    "Tamil": {"Safe": "பாதுகாப்பான", "Moderate": "மிதமான", "High": "உயர்"},
    "Marathi": {"Safe": "सुरक्षित", "Moderate": "मध्यम", "High": "उच्च"}
}

# Pie chart labels translations
PIE_LABEL_TRANSLATIONS = {
    "English": {
        "Water Scarcity": "Water Scarcity",
        "Temperature Stress": "Temperature Stress", 
        "Crop Demand": "Crop Demand",
        "Normal": "Normal"
    },
    "Hindi": {
        "Water Scarcity": "जल की कमी",
        "Temperature Stress": "तापमान तनाव",
        "Crop Demand": "फसल की मांग",
        "Normal": "सामान्य"
    },
    "Kannada": {
        "Water Scarcity": "ನೀರಿನ ಕೊರತೆ",
        "Temperature Stress": "ತಾಪಮಾನ ಒತ್ತಡ",
        "Crop Demand": "ಬೆಳೆಯ ಬೇಡಿಕೆ",
        "Normal": "ಸಾಮಾನ್ಯ"
    },
    "Telugu": {
        "Water Scarcity": "నీటి కొరత",
        "Temperature Stress": "ఉష్ణోగ్రత ఒత్తిడి",
        "Crop Demand": "పంట డిమాండ్",
        "Normal": "సాధారణ"
    },
    "Tamil": {
        "Water Scarcity": "நீர் பற்றாக்குறை",
        "Temperature Stress": "வெப்பநிலை அழுத்தம்",
        "Crop Demand": "பயிர் தேவை",
        "Normal": "சாதாரண"
    },
    "Marathi": {
        "Water Scarcity": "पाण्याची कमतरता",
        "Temperature Stress": "तापमान ताण",
        "Crop Demand": "पिकाची मागणी",
        "Normal": "सामान्य"
    }
}

# Recommendations translations
RECOMMENDATIONS_TRANSLATIONS = {
    "English": {
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
    },
    "Hindi": {
        "High": [
            "🚨 तत्काल: सभी गैर-जरूरी पानी का उपयोग बंद करें",
            "💧 ड्रिप सिंचाई पर स्विच करें (50% पानी बचाता है)",
            "🌾 सूखा प्रतिरोधी बाजरा या ज्वार बोएं",
            "📊 प्रतिदिन भूजल स्तर की निगरानी करें",
            "🌧️ तत्काल वर्षा जल संचयन लागू करें"
        ],
        "Moderate": [
            "⚠️ सिंचाई 25-30% कम करें",
            "💧 मिट्टी की नमी सेंसर लगाएं",
            "🔄 कम पानी वाली फसलों के साथ बदलाव करें",
            "📈 नमी बनाए रखने के लिए मल्चिंग करें",
            "💦 सुबह या शाम को सिंचाई करें"
        ],
        "Safe": [
            "✅ वर्तमान सिंचाई पद्धतियाँ जारी रखें",
            "💧 नियमित जल स्तर की निगरानी बनाए रखें",
            "🌧️ वर्षा जल संचयन क्षमता बढ़ाएं",
            "📊 पानी के उपयोग के रिकॉर्ड रखें",
            "🌱 अधिक पानी वाली फसलों के लिए अच्छा समय"
        ]
    },
    "Kannada": {
        "High": [
            "🚨 ತಕ್ಷಣ: ಎಲ್ಲಾ ಅನಗತ್ಯ ನೀರಿನ ಬಳಕೆಯನ್ನು ನಿಲ್ಲಿಸಿ",
            "💧 ಹನಿ ನೀರಾವರಿಗೆ ಬದಲಿಸಿ (50% ನೀರು ಉಳಿಸುತ್ತದೆ)",
            "🌾 ಬರ-ನಿರೋಧಕ ರಾಗಿ ಅಥವಾ ಜೋಳವನ್ನು ಬೆಳೆಯಿರಿ",
            "📊 ಪ್ರತಿದಿನ ಅಂತರ್ಜಲ ಮಟ್ಟವನ್ನು ಮೇಲ್ವಿಚಾರಣೆ ಮಾಡಿ",
            "🌧️ ತಕ್ಷಣ ಮಳೆನೀರು ಕೊಯ್ಲು ಅಳವಡಿಸಿ"
        ],
        "Moderate": [
            "⚠️ ನೀರಾವರಿಯನ್ನು 25-30% ರಷ್ಟು ಕಡಿಮೆ ಮಾಡಿ",
            "💧 ಮಣ್ಣಿನ ತೇವಾಂಶ ಸಂವೇದಕಗಳನ್ನು ಸ್ಥಾಪಿಸಿ",
            "🔄 ಕಡಿಮೆ ನೀರು ಬಳಸುವ ಬೆಳೆಗಳೊಂದಿಗೆ ಪರ್ಯಾಯ ಮಾಡಿ",
            "📈 ತೇವಾಂಶ ಉಳಿಸಿಕೊಳ್ಳಲು ಮಲ್ಚಿಂಗ್ ಮಾಡಿ",
            "💦 ಬೆಳಿಗ್ಗೆ ಅಥವಾ ಸಂಜೆ ನೀರಾವರಿ ಮಾಡಿ"
        ],
        "Safe": [
            "✅ ಪ್ರಸ್ತುತ ನೀರಾವರಿ ಅಭ್ಯಾಸಗಳನ್ನು ಮುಂದುವರಿಸಿ",
            "💧 ನಿಯಮಿತ ನೀರಿನ ಮಟ್ಟದ ಮೇಲ್ವಿಚಾರಣೆ ಕಾಪಾಡಿಕೊಳ್ಳಿ",
            "🌧️ ಮಳೆನೀರು ಕೊಯ್ಲು ಸಾಮರ್ಥ್ಯವನ್ನು ವಿಸ್ತರಿಸಿ",
            "📊 ನೀರಿನ ಬಳಕೆಯ ದಾಖಲೆಗಳನ್ನು ಇರಿಸಿ",
            "🌱 ಹೆಚ್ಚು ನೀರು ಬೇಡುವ ಬೆಳೆಗಳಿಗೆ ಉತ್ತಮ ಸಮಯ"
        ]
    },
    "Telugu": {
        "High": [
            "🚨 వెంటనే: అన్ని అనవసర నీటి వినియోగాన్ని ఆపండి",
            "💧 బిందు సేద్యానికి మారండి (50% నీరు ఆదా చేస్తుంది)",
            "🌾 కరువు-నిరోధక జొన్నలు లేదా సజ్జలు పండించండి",
            "📊 ప్రతిరోజూ భూగర్భ జలాల స్థాయిలను పర్యవేక్షించండి",
            "🌧️ వెంటనే వర్షపు నీటి సేకరణను అమలు చేయండి"
        ],
        "Moderate": [
            "⚠️ సేద్యాన్ని 25-30% తగ్గించండి",
            "💧 నేల తేమ సెన్సార్లను ఏర్పాటు చేయండి",
            "🔄 తక్కువ నీరు వాడే పంటలతో మార్పు చేయండి",
            "📈 తేమ నిలుపుకోవడానికి మల్చింగ్ చేయండి",
            "💦 ఉదయం లేదా సాయంత్రం సేద్యం చేయండి"
        ],
        "Safe": [
            "✅ ప్రస్తుత సేద్యం పద్ధతులను కొనసాగించండి",
            "💧 క్రమం తప్పకుండా నీటి మట్టాలను పర్యవేక్షించండి",
            "🌧️ వర్షపు నీటి సేకరణ సామర్థ్యాన్ని విస్తరించండి",
            "📊 నీటి వినియోగ రికార్డులను ఉంచండి",
            "🌱 ఎక్కువ నీరు వాడే పంటలకు మంచి సమయం"
        ]
    },
    "Tamil": {
        "High": [
            "🚨 உடனடி: அனைத்து தேவையற்ற நீர் பயன்பாட்டையும் நிறுத்துங்கள்",
            "💧 சொட்டு நீர்ப்பாசனத்திற்கு மாறுங்கள் (50% நீர் மிச்சமாகும்)",
            "🌾 வறட்சியை எதிர்க்கும் தினை அல்லது சோளத்தை பயிரிடுங்கள்",
            "📊 தினமும் நிலத்தடி நீர் மட்டங்களை கண்காணிக்கவும்",
            "🌧️ உடனடியாக மழைநீர் சேகரிப்பை செயல்படுத்துங்கள்"
        ],
        "Moderate": [
            "⚠️ நீர்ப்பாசனத்தை 25-30% குறைக்கவும்",
            "💧 மண்ணின் ஈரப்பதம் சென்சார்களை நிறுவுங்கள்",
            "🔄 குறைந்த நீர் பயன்படுத்தும் பயிர்களுடன் மாற்றுங்கள்",
            "📈 ஈரப்பதத்தை தக்கவைக்க மல்ச்சிங் செய்யுங்கள்",
            "💦 காலை அல்லது மாலையில் நீர்ப்பாசனம் செய்யுங்கள்"
        ],
        "Safe": [
            "✅ தற்போதைய நீர்ப்பாசன நடைமுறைகளை தொடருங்கள்",
            "💧 வழக்கமான நீர் மட்ட கண்காணிப்பை பராமரிக்கவும்",
            "🌧️ மழைநீர் சேகரிப்பு திறனை விரிவாக்குங்கள்",
            "📊 நீர் பயன்பாட்டு பதிவுகளை வைத்திருங்கள்",
            "🌱 அதிக நீர் தேவைப்படும் பயிர்களுக்கு நல்ல நேரம்"
        ]
    },
    "Marathi": {
        "High": [
            "🚨 त्वरित: सर्व अनावश्यक पाण्याचा वापर थांबवा",
            "💧 ठिबक सिंचनाकडे स्विच करा (50% पाणी वाचवते)",
            "🌾 दुष्काळ-प्रतिरोधक बाजरी किंवा ज्वारी पिकवा",
            "📊 दररोज भूजल पातळीचे निरीक्षण करा",
            "🌧️ त्वरित पावसाचे पाणी साठवण लागू करा"
        ],
        "Moderate": [
            "⚠️ सिंचन 25-30% कमी करा",
            "💧 माती ओलावा सेन्सर बसवा",
            "🔄 कमी पाणी वापरणाऱ्या पिकांसह फेरपालट करा",
            "📈 ओलावा टिकवण्यासाठी मल्चिंग करा",
            "💦 सकाळी किंवा संध्याकाळी सिंचन करा"
        ],
        "Safe": [
            "✅ सध्याच्या सिंचन पद्धती सुरू ठेवा",
            "💧 नियमित पाण्याच्या पातळीचे निरीक्षण राखा",
            "🌧️ पावसाचे पाणी साठवण क्षमता वाढवा",
            "📊 पाण्याच्या वापराच्या नोंदी ठेवा",
            "🌱 जास्त पाणी वापरणाऱ्या पिकांसाठी चांगली वेळ"
        ]
    }
}

# AI Chatbot responses in multiple languages
AI_RESPONSES_TRANSLATIONS = {
    "English": {
        "rainfall": "🌧️ **Rainfall Management Tips:**\n\n• Install rain gauges to measure daily rainfall\n• Create farm ponds to store excess rainwater\n• Use drip irrigation during dry spells\n• Practice mulching to retain soil moisture\n• Consider contour farming to reduce runoff\n\n**Best practice:** Harvest every drop of rainwater through rooftop harvesting and farm ponds!",
        
        "crops": "🌾 **Best Crops for Dry Regions:**\n\n**Drought-resistant crops (40-60% less water):**\n• Millets (Jowar, Bajra, Ragi) - 350mm water\n• Sorghum - 400mm water\n• Pulses (Tur, Moong, Chana) - 350mm water\n• Groundnut - 400mm water\n• Cotton - 500mm water\n\n**Avoid:** Rice (1200mm), Sugarcane (1800mm)",
        
        "water": "💧 **Water Conservation Techniques:**\n\n1. Drip irrigation - saves 50-70% water\n2. Mulching - reduces evaporation by 70%\n3. Rainwater harvesting - collect 100% runoff\n4. Contour farming - prevents runoff\n5. Cover cropping - improves soil moisture\n\n**Pro tip:** Water at sunrise or sunset to reduce evaporation loss by 30%!",
        
        "temperature": "🌡️ **High Temperature Management:**\n\n• Use shade nets (40-50% shade) for vegetables\n• Increase irrigation frequency but reduce quantity\n• Apply kaolin clay on leaves\n• Schedule farming: 6-9 AM or 5-7 PM\n• Grow heat-tolerant varieties\n\n**Critical:** When temperature > 38°C, stop fertilizer application!",
        
        "default": "🤖 **I'm AquaGuard AI, your agricultural expert!**\n\nI can help you with:\n\n🌧️ Rainfall management\n💧 Groundwater conservation\n🌾 Crop selection for dry regions\n🌡️ Temperature effects on crops\n💦 Efficient irrigation methods\n🌱 Soil health improvement\n\n**Just ask me anything about farming!**"
    },
    "Hindi": {
        "rainfall": "🌧️ **वर्षा प्रबंधन टिप्स:**\n\n• दैनिक वर्षा मापने के लिए रेन गेज लगाएं\n• अतिरिक्त वर्षा जल संग्रह के लिए फार्म तालाब बनाएं\n• सूखे के दौरान ड्रिप सिंचाई का उपयोग करें\n• मिट्टी की नमी बनाए रखने के लिए मल्चिंग करें\n• अपवाह कम करने के लिए कंटूर फार्मिंग करें\n\n**सर्वोत्तम अभ्यास:** छत संग्रहण और फार्म तालाबों के माध्यम से हर बूंद वर्षा जल एकत्र करें!",
        
        "crops": "🌾 **सूखे क्षेत्रों के लिए सर्वोत्तम फसलें:**\n\n**सूखा प्रतिरोधी फसलें (40-60% कम पानी):**\n• बाजरा, ज्वार, रागी - 350mm पानी\n• ज्वार - 400mm पानी\n• दालें (तूर, मूंग, चना) - 350mm पानी\n• मूंगफली - 400mm पानी\n• कपास - 500mm पानी\n\n**टालें:** चावल (1200mm), गन्ना (1800mm)",
        
        "water": "💧 **जल संरक्षण तकनीकें:**\n\n1. ड्रिप सिंचाई - 50-70% पानी बचाती है\n2. मल्चिंग - वाष्पीकरण 70% कम करती है\n3. वर्षा जल संचयन - 100% अपवाह एकत्र करें\n4. कंटूर फार्मिंग - अपवाह रोकती है\n5. कवर क्रॉपिंग - मिट्टी की नमी बढ़ाती है\n\n**टिप:** सूर्योदय या सूर्यास्त के समय पानी दें, वाष्पीकरण 30% कम होगा!",
        
        "temperature": "🌡️ **उच्च तापमान प्रबंधन:**\n\n• सब्जियों के लिए शेड नेट (40-50% छाया) का उपयोग करें\n• सिंचाई आवृत्ति बढ़ाएं लेकिन मात्रा कम करें\n• पत्तियों पर काओलिन मिट्टी लगाएं\n• खेती का समय: सुबह 6-9 बजे या शाम 5-7 बजे\n• गर्मी सहनशील किस्में उगाएं\n\n**महत्वपूर्ण:** जब तापमान 38°C से अधिक हो, उर्वरक का उपयोग बंद कर दें!",
        
        "default": "🤖 **मैं एक्वागार्ड एआई हूं, आपका कृषि विशेषज्ञ!**\n\nमैं आपकी मदद कर सकता हूं:\n\n🌧️ वर्षा प्रबंधन\n💧 भूजल संरक्षण\n🌾 सूखे क्षेत्रों के लिए फसल चयन\n🌡️ फसलों पर तापमान प्रभाव\n💦 कुशल सिंचाई विधियाँ\n🌱 मिट्टी स्वास्थ्य सुधार\n\n**बस मुझसे खेती के बारे में कुछ भी पूछें!**"
    },
    "Kannada": {
        "rainfall": "🌧️ **ಮಳೆ ನಿರ್ವಹಣಾ ಸಲಹೆಗಳು:**\n\n• ದೈನಂದಿನ ಮಳೆ ಅಳೆಯಲು ರೇನ್ ಗೇಜ್ ಅಳವಡಿಸಿ\n• ಹೆಚ್ಚುವರಿ ಮಳೆನೀರು ಸಂಗ್ರಹಕ್ಕೆ ಕೊಳಗಳನ್ನು ನಿರ್ಮಿಸಿ\n• ಬರಗಾಲದ ಸಮಯದಲ್ಲಿ ಹನಿ ನೀರಾವರಿ ಬಳಸಿ\n• ಮಣ್ಣಿನ ತೇವಾಂಶ ಉಳಿಸಿಕೊಳ್ಳಲು ಮಲ್ಚಿಂಗ್ ಮಾಡಿ\n• ನೀರು ಹರಿದು ಹೋಗದಂತೆ ಬಾಹುಬಲಿ ಕೃಷಿ ಮಾಡಿ\n\n**ಉತ್ತಮ ಅಭ್ಯಾಸ:** ಮಳೆಯ ಪ್ರತಿ ಹನಿಯನ್ನು ಸಂಗ್ರಹಿಸಿ!",
        
        "crops": "🌾 **ಬರಗಾಲ ಪ್ರದೇಶಗಳಿಗೆ ಉತ್ತಮ ಬೆಳೆಗಳು:**\n\n**ಬರ-ನಿರೋಧಕ ಬೆಳೆಗಳು (40-60% ಕಡಿಮೆ ನೀರು):**\n• ರಾಗಿ, ಜೋಳ, ನವಣೆ - 350mm ನೀರು\n• ಜೋಳ - 400mm ನೀರು\n• ದ್ವಿದಳ ಧಾನ್ಯಗಳು (ತೊಗರಿ, ಹೆಸರು, ಕಡಲೆ) - 350mm ನೀರು\n• ಕಡಲೆಕಾಯಿ - 400mm ನೀರು\n• ಹತ್ತಿ - 500mm ನೀರು\n\n**ತಪ್ಪಿಸಿ:** ಭತ್ತ (1200mm), ಕಬ್ಬು (1800mm)",
        
        "water": "💧 **ನೀರು ಸಂರಕ್ಷಣಾ ತಂತ್ರಗಳು:**\n\n1. ಹನಿ ನೀರಾವರಿ - 50-70% ನೀರು ಉಳಿಸುತ್ತದೆ\n2. ಮಲ್ಚಿಂಗ್ - ಆವಿಯಾಗುವಿಕೆ 70% ಕಡಿಮೆ ಮಾಡುತ್ತದೆ\n3. ಮಳೆನೀರು ಕೊಯ್ಲು - 100% ಸಂಗ್ರಹಿಸಿ\n4. ಬಾಹುಬಲಿ ಕೃಷಿ - ನೀರು ಹರಿಯದಂತೆ ತಡೆಯುತ್ತದೆ\n5. ಹಸಿರು ಸಸ್ಯಗಳು - ಮಣ್ಣಿನ ತೇವಾಂಶ ಹೆಚ್ಚಿಸುತ್ತದೆ\n\n**ಸಲಹೆ:** ಸೂರ್ಯೋದಯ ಅಥವಾ ಸೂರ್ಯಾಸ್ತದ ಸಮಯದಲ್ಲಿ ನೀರು ಹಾಕಿ, ಆವಿಯಾಗುವಿಕೆ 30% ಕಡಿಮೆಯಾಗುತ್ತದೆ!",
        
        "temperature": "🌡️ **ಹೆಚ್ಚಿನ ತಾಪಮಾನ ನಿರ್ವಹಣೆ:**\n\n• ತರಕಾರಿಗಳಿಗೆ ಛಾವಣಿಯ ನೆಟ್ (40-50% ನೆರಳು) ಬಳಸಿ\n• ನೀರಾವರಿ ಪ್ರಮಾಣ ಕಡಿಮೆ ಮಾಡಿ, ಆದರೆ ಆವರ್ತನ ಹೆಚ್ಚಿಸಿ\n• ಎಲೆಗಳ ಮೇಲೆ ಕಯೋಲಿನ್ ಮಣ್ಣನ್ನು ಹಚ್ಚಿ\n• ಕೃಷಿ ಸಮಯ: ಬೆಳಿಗ್ಗೆ 6-9 ಅಥವಾ ಸಂಜೆ 5-7\n• ಶಾಖ ಸಹಿಷ್ಣು ಪ್ರಭೇದಗಳನ್ನು ಬೆಳೆಯಿರಿ\n\n**ಪ್ರಮುಖ:** ತಾಪಮಾನ 38°C ಮೀರಿದಾಗ, ಗೊಬ್ಬರ ಹಾಕುವುದನ್ನು ನಿಲ್ಲಿಸಿ!",
        
        "default": "🤖 **ನಾನು ಅಕ್ವಾಗಾರ್ಡ್ ಎಐ, ನಿಮ್ಮ ಕೃಷಿ ತಜ್ಞ!**\n\nನಾನು ನಿಮಗೆ ಸಹಾಯ ಮಾಡಬಲ್ಲೆ:\n\n🌧️ ಮಳೆ ನಿರ್ವಹಣೆ\n💧 ಅಂತರ್ಜಲ ಸಂರಕ್ಷಣೆ\n🌾 ಬರಗಾಲ ಪ್ರದೇಶಗಳಿಗೆ ಬೆಳೆ ಆಯ್ಕೆ\n🌡️ ಬೆಳೆಗಳ ಮೇಲೆ ತಾಪಮಾನ ಪರಿಣಾಮ\n💦 ಸಮರ್ಥ ನೀರಾವರಿ ವಿಧಾನಗಳು\n🌱 ಮಣ್ಣಿನ ಆರೋಗ್ಯ ಸುಧಾರಣೆ\n\n**ಕೃಷಿಯ ಬಗ್ಗೆ ನನ್ನನ್ನು ಏನು ಬೇಕಾದರೂ ಕೇಳಿ!**"
    },
    "Telugu": {
        "rainfall": "🌧️ **వర్షపాతం నిర్వహణ చిట్కాలు:**\n\n• రోజువారీ వర్షపాతం కొలవడానికి రేన్ గేజ్ ఏర్పాటు చేయండి\n• అదనపు వర్షపు నీటి నిల్వకు చెరువులు నిర్మించండి\n• కరువు సమయంలో బిందు సేద్యం ఉపయోగించండి\n• నేల తేమ నిలుపుకోవడానికి మల్చింగ్ చేయండి\n• నీరు కారకుండా కాంటూర్ ఫార్మింగ్ చేయండి\n\n**ఉత్తమ పద్ధతి:** ప్రతి చుక్క వర్షపు నీటిని సేకరించండి!",
        
        "crops": "🌾 **ఎండ ప్రాంతాలకు ఉత్తమ పంటలు:**\n\n**కరువు-నిరోధక పంటలు (40-60% తక్కువ నీరు):**\n• జొన్నలు, సజ్జలు, రాగులు - 350mm నీరు\n• జొన్న - 400mm నీరు\n• చిక్కుడు, మినుములు, శనగలు - 350mm నీరు\n• వేరుశెనగ - 400mm నీరు\n• పత్తి - 500mm నీరు\n\n**నివారించండి:** వరి (1200mm), చెరకు (1800mm)",
        
        "water": "💧 **నీటి పరిరక్షణ పద్ధతులు:**\n\n1. బిందు సేద్యం - 50-70% నీరు ఆదా చేస్తుంది\n2. మల్చింగ్ - ఆవిరిని 70% తగ్గిస్తుంది\n3. వర్షపు నీటి సేకరణ - 100% సేకరించండి\n4. కాంటూర్ ఫార్మింగ్ - నీరు కారకుండా నిరోధిస్తుంది\n5. కవర్ క్రాపింగ్ - నేల తేమను మెరుగుపరుస్తుంది\n\n**చిట్కా:** సూర్యోదయం లేదా సూర్యాస్తమయం సమయంలో నీరు పెట్టండి, ఆవిరి 30% తగ్గుతుంది!",
        
        "temperature": "🌡️ **అధిక ఉష్ణోగ్రత నిర్వహణ:**\n\n• కూరగాయలకు షేడ్ నెట్లు (40-50% నీడ) ఉపయోగించండి\n• సేద్యం తరచుదనం పెంచండి కానీ పరిమాణం తగ్గించండి\n• ఆకులపై కయోలిన్ మట్టి రాయండి\n• వ్యవసాయ సమయం: ఉదయం 6-9 లేదా సాయంత్రం 5-7\n• వేడిని తట్టుకునే రకాలను పండించండి\n\n**క్లిష్టమైన:** ఉష్ణోగ్రత 38°C మీరినప్పుడు, ఎరువుల వాడకం ఆపండి!",
        
        "default": "🤖 **నేను అక్వాగార్డ్ ఏఐ, మీ వ్యవసాయ నిపుణుడిని!**\n\nనేను మీకు సహాయం చేయగలను:\n\n🌧️ వర్షపాతం నిర్వహణ\n💧 భూగర్భ జలాల పరిరక్షణ\n🌾 ఎండ ప్రాంతాలకు పంటల ఎంపిక\n🌡️ పంటలపై ఉష్ణోగ్రత ప్రభావం\n💦 సమర్థవంతమైన సేద్యం పద్ధతులు\n🌱 నేల ఆరోగ్య మెరుగుదల\n\n**వ్యవసాయం గురించి నన్ను ఏదైనా అడగండి!**"
    },
    "Tamil": {
        "rainfall": "🌧️ **மழைப்பொழிவு மேலாண்மை உதவிக்குறிப்புகள்:**\n\n• தினசரி மழையை அளக்க ரெயின் கேஜ் நிறுவுங்கள்\n• அதிகப்படியான மழைநீர் சேமிப்புக்கு குளங்களை உருவாக்குங்கள்\n• வறட்சியின் போது சொட்டு நீர்ப்பாசனம் பயன்படுத்துங்கள்\n• மண்ணின் ஈரப்பதத்தை தக்கவைக்க மல்ச்சிங் செய்யுங்கள்\n• நீர் வடிதலைத் தடுக்க கான்டூர் ஃபார்மிங் செய்யுங்கள்\n\n**சிறந்த நடைமுறை:** மழையின் ஒவ்வொரு துளியையும் சேகரிக்கவும்!",
        
        "crops": "🌾 **வறண்ட பகுதிகளுக்கு சிறந்த பயிர்கள்:**\n\n**வறட்சியை எதிர்க்கும் பயிர்கள் (40-60% குறைந்த நீர்):**\n• தினை, சோளம், கேழ்வரகு - 350mm நீர்\n• சோளம் - 400mm நீர்\n• பருப்பு வகைகள் - 350mm நீர்\n• நிலக்கடலை - 400mm நீர்\n• பருத்தி - 500mm நீர்\n\n**தவிர்க்கவும்:** நெல் (1200mm), கரும்பு (1800mm)",
        
        "water": "💧 **நீர் பாதுகாப்பு நுட்பங்கள்:**\n\n1. சொட்டு நீர்ப்பாசனம் - 50-70% நீரை சேமிக்கும்\n2. மல்ச்சிங் - ஆவியாவதை 70% குறைக்கும்\n3. மழைநீர் சேகரிப்பு - 100% சேகரிக்கவும்\n4. கான்டூர் ஃபார்மிங் - நீர் வடிதலைத் தடுக்கும்\n5. கவர் கிராப்பிங் - மண்ணின் ஈரப்பதத்தை மேம்படுத்தும்\n\n**உதவிக்குறிப்பு:** சூரியோதயம் அல்லது சூரியாஸ்தமனத்தில் நீர்ப்பாசனம் செய்யுங்கள், ஆவியாதல் 30% குறையும்!",
        
        "temperature": "🌡️ **அதிக வெப்பநிலை மேலாண்மை:**\n\n• காய்கறிகளுக்கு ஷேட் நெட்களை (40-50% நிழல்) பயன்படுத்துங்கள்\n• நீர்ப்பாசன அளவை குறைத்து, அதிர்வெண்ணை அதிகரிக்கவும்\n• இலைகளில் கயோலின் களிமண்ணை பூசுங்கள்\n• பண்ணை நேரம்: காலை 6-9 அல்லது மாலை 5-7\n• வெப்பத்தை தாங்கும் ரகங்களை பயிரிடுங்கள்\n\n**முக்கியமான:** வெப்பநிலை 38°C க்கு மேல் இருக்கும்போது, உர பயன்பாட்டை நிறுத்தவும்!",
        
        "default": "🤖 **நான் அக்வாகார்ட் ஏஐ, உங்கள் வேளாண் நிபுணர்!**\n\nநான் உங்களுக்கு உதவ முடியும்:\n\n🌧️ மழைப்பொழிவு மேலாண்மை\n💧 நிலத்தடி நீர் பாதுகாப்பு\n🌾 வறண்ட பகுதிகளுக்கு பயிர் தேர்வு\n🌡️ பயிர்களில் வெப்பநிலை விளைவுகள்\n💦 திறமையான நீர்ப்பாசன முறைகள்\n🌱 மண் ஆரோக்கிய மேம்பாடு\n\n**வேளாண்மை பற்றி என்னை எதுவும் கேளுங்கள்!**"
    },
    "Marathi": {
        "rainfall": "🌧️ **पाऊस व्यवस्थापन टिप्स:**\n\n• दैनंदिन पाऊस मोजण्यासाठी रेन गेज लावा\n• अतिरिक्त पावसाचे पाणी साठवण्यासाठी शेततळी बनवा\n• दुष्काळात ठिबक सिंचन वापरा\n• मातीतील ओलावा टिकवण्यासाठी मल्चिंग करा\n• पाणी वाहून जाण्यापासून रोखण्यासाठी कॉन्टूर फार्मिंग करा\n\n**उत्तम पद्धत:** पावसाचा प्रत्येक थेंब साठवा!",
        
        "crops": "🌾 **कोरडवाहू भागांसाठी उत्तम पिके:**\n\n**दुष्काळ-प्रतिरोधक पिके (40-60% कमी पाणी):**\n• बाजरी, ज्वारी, नाचणी - 350mm पाणी\n• ज्वारी - 400mm पाणी\n• डाळी (तूर, मूग, चणे) - 350mm पाणी\n• शेंगदाणा - 400mm पाणी\n• कापूस - 500mm पाणी\n\n**टाळा:** भात (1200mm), उस (1800mm)",
        
        "water": "💧 **जलसंधारण तंत्रे:**\n\n1. ठिबक सिंचन - 50-70% पाणी वाचवते\n2. मल्चिंग - बाष्पीभवन 70% कमी करते\n3. पावसाचे पाणी साठवण - 100% साठवा\n4. कॉन्टूर फार्मिंग - पाणी वाहून जाण्यापासून रोखते\n5. कव्हर क्रॉपिंग - मातीतील ओलावा वाढवते\n\n**टिप:** सूर्योदय किंवा सूर्यास्ताच्या वेळी पाणी द्या, बाष्पीभवन 30% कमी होईल!",
        
        "temperature": "🌡️ **उच्च तापमान व्यवस्थापन:**\n\n• भाज्यांसाठी शेड नेट्स (40-50% सावली) वापरा\n• सिंचन प्रमाण कमी करा पण वारंवारता वाढवा\n• पानांवर काओलिन माती लावा\n• शेतीची वेळ: सकाळी 6-9 किंवा संध्याकाळी 5-7\n• उष्णता सहनशील वाणांची लागवड करा\n\n**गंभीर:** तापमान 38°C पेक्षा जास्त असेल तेव्हा खत वापरणे थांबवा!",
        
        "default": "🤖 **मी अक्वागार्ड एआय, तुमचा कृषी तज्ञ!**\n\nमी तुम्हाला मदत करू शकतो:\n\n🌧️ पाऊस व्यवस्थापन\n💧 भूजल संरक्षण\n🌾 कोरडवाहू भागांसाठी पीक निवड\n🌡️ पिकांवर तापमानाचे परिणाम\n💦 कार्यक्षम सिंचन पद्धती\n🌱 माती आरोग्य सुधारणा\n\n**शेतीबद्दल मला काहीही विचारा!**"
    }
}

def get_ai_response(question, lang):
    """Get AI response in selected language"""
    q = question.lower()
    responses = AI_RESPONSES_TRANSLATIONS.get(lang, AI_RESPONSES_TRANSLATIONS["English"])
    
    if "rainfall" in q or "rain" in q or "पाऊस" in q or "ಮಳೆ" in q:
        return responses["rainfall"]
    elif "crop" in q or "फसल" in q or "ಬೆಳೆ" in q or "పంట" in q:
        return responses["crops"]
    elif "water" in q or "पाणी" in q or "ನೀರು" in q or "నీరు" in q:
        return responses["water"]
    elif "temperature" in q or "तापमान" in q or "ತಾಪಮಾನ" in q:
        return responses["temperature"]
    else:
        return responses["default"]

def t(key):
    """Get translated UI text"""
    return UI_TRANSLATIONS.get(st.session_state["lang"], UI_TRANSLATIONS["English"]).get(key, key)

def localize_region(region):
    return REGION_TRANSLATIONS.get(st.session_state["lang"], REGION_TRANSLATIONS["English"]).get(region, region)

def localize_crop(crop):
    return CROP_TRANSLATIONS.get(st.session_state["lang"], CROP_TRANSLATIONS["English"]).get(crop, crop)

def localize_season(season):
    return SEASON_TRANSLATIONS.get(st.session_state["lang"], SEASON_TRANSLATIONS["English"]).get(season, season)

def localize_status(status):
    return STATUS_TRANSLATIONS.get(st.session_state["lang"], STATUS_TRANSLATIONS["English"]).get(status, status)

def localize_pie_label(label):
    return PIE_LABEL_TRANSLATIONS.get(st.session_state["lang"], PIE_LABEL_TRANSLATIONS["English"]).get(label, label)

def get_localized_recommendations(risk_level):
    """Get recommendations in selected language"""
    recs = RECOMMENDATIONS_TRANSLATIONS.get(st.session_state["lang"], RECOMMENDATIONS_TRANSLATIONS["English"])
    return recs.get(risk_level, recs["Safe"])

# UI translations
UI_TRANSLATIONS = {
    "English": {
        "app_title": "AquaGuard AI",
        "tagline": "Smart Groundwater Management System",
        "welcome": "Welcome",
        "dashboard": "Home Dashboard",
        "analytics": "Analytics & Insights",
        "consultant": "AI Consultant",
        "settings": "Profile Settings",
        "logout": "Logout",
        "region": "Region",
        "season": "Season",
        "crop": "Crop Type",
        "rainfall": "Rainfall (mm)",
        "temperature": "Temperature (°C)",
        "rainfall_trend": "Past Rainfall Trend (mm)",
        "borewell": "Borewell Dependency (%)",
        "analyze": "Run Analysis & Prediction",
        "system_status": "System Status",
        "api_status": "API Status",
        "active_region": "Active Region",
        "connection": "Connection",
        "pro_tip": "Pro Tip",
        "risk_level": "Risk Level",
        "status": "Status",
        "explanation": "Analysis",
        "recommendations": "Expert Recommendations",
        "groundwater_forecast": "Groundwater Depth Forecast",
        "rainfall_forecast": "Rainfall Prediction",
        "temperature_forecast": "Temperature Prediction",
        "risk_distribution": "Risk Distribution Analysis",
        "ask_btn": "Get Expert Advice",
        "quick_questions": "Quick Questions",
        "ask_anything": "Ask me anything about farming, water management, or crops:",
        "current_water_level": "Current Water Level",
        "current_temp": "Current Temp",
        "below_ground": "Below ground",
        "air_temperature": "Air temperature",
        "online": "Online",
        "secure": "Secure",
        "analysis_complete": "Analysis complete! Check Analytics & Insights for detailed charts.",
        "no_data": "No data found. Please run analysis on the Home Dashboard first.",
        "preferences_updated": "Preferences updated!",
        "password_updated": "Password updated!",
        "save_preferences": "Save Preferences",
        "favorite_region": "Favorite Region",
        "regional_preferences": "Regional Preferences",
        "security": "Security",
        "current_password": "Current Password",
        "new_password": "New Password",
        "update_password": "Update Password",
        "login": "Login",
        "signup": "Sign Up",
        "username": "Username",
        "email": "Email",
        "password": "Password",
        "access_dashboard": "Access Dashboard",
        "create_account": "Create Account"
    },
    "Hindi": {
        "app_title": "एक्वागार्ड एआई",
        "tagline": "स्मार्ट भूजल प्रबंधन प्रणाली",
        "welcome": "स्वागत है",
        "dashboard": "मुख्य डैशबोर्ड",
        "analytics": "विश्लेषण और अंतर्दृष्टि",
        "consultant": "एआई सलाहकार",
        "settings": "प्रोफ़ाइल सेटिंग्स",
        "logout": "लॉग आउट",
        "region": "क्षेत्र",
        "season": "मौसम",
        "crop": "फसल का प्रकार",
        "rainfall": "वर्षा (मिमी)",
        "temperature": "तापमान (°C)",
        "rainfall_trend": "पिछला वर्षा रुझान (मिमी)",
        "borewell": "बोरवेल निर्भरता (%)",
        "analyze": "विश्लेषण और भविष्यवाणी करें",
        "system_status": "सिस्टम स्थिति",
        "api_status": "एपीआई स्थिति",
        "active_region": "सक्रिय क्षेत्र",
        "connection": "कनेक्शन",
        "pro_tip": "विशेष सुझाव",
        "risk_level": "जोखिम स्तर",
        "status": "स्थिति",
        "explanation": "विश्लेषण",
        "recommendations": "विशेषज्ञ सुझाव",
        "groundwater_forecast": "भूजल गहराई पूर्वानुमान",
        "rainfall_forecast": "वर्षा पूर्वानुमान",
        "temperature_forecast": "तापमान पूर्वानुमान",
        "risk_distribution": "जोखिम वितरण विश्लेषण",
        "ask_btn": "विशेषज्ञ सलाह लें",
        "quick_questions": "त्वरित प्रश्न",
        "ask_anything": "फसल प्रबंधन, जल संरक्षण, या कृषि पद्धतियों के बारे में पूछें:",
        "current_water_level": "वर्तमान जल स्तर",
        "current_temp": "वर्तमान तापमान",
        "below_ground": "जमीन के नीचे",
        "air_temperature": "हवा का तापमान",
        "online": "ऑनलाइन",
        "secure": "सुरक्षित",
        "analysis_complete": "विश्लेषण पूर्ण! विस्तृत चार्ट के लिए एनालिटिक्स देखें।",
        "no_data": "कोई डेटा नहीं मिला। कृपया पहले होम डैशबोर्ड पर विश्लेषण चलाएं।",
        "preferences_updated": "प्राथमिकताएं अपडेट हुईं!",
        "password_updated": "पासवर्ड अपडेट हुआ!",
        "save_preferences": "प्राथमिकताएं सहेजें",
        "favorite_region": "पसंदीदा क्षेत्र",
        "regional_preferences": "क्षेत्रीय प्राथमिकताएं",
        "security": "सुरक्षा",
        "current_password": "वर्तमान पासवर्ड",
        "new_password": "नया पासवर्ड",
        "update_password": "पासवर्ड अपडेट करें",
        "login": "लॉगिन",
        "signup": "साइनअप",
        "username": "उपयोगकर्ता नाम",
        "email": "ईमेल",
        "password": "पासवर्ड",
        "access_dashboard": "डैशबोर्ड तक पहुंचें",
        "create_account": "खाता बनाएं"
    },
    "Kannada": {
        "app_title": "ಅಕ್ವಾಗಾರ್ಡ್ ಎಐ",
        "tagline": "ಸ್ಮಾರ್ಟ್ ಅಂತರ್ಜಲ ನಿರ್ವಹಣಾ ವ್ಯವಸ್ಥೆ",
        "welcome": "ಸ್ವಾಗತ",
        "dashboard": "ಮುಖ್ಯ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",
        "analytics": "ವಿಶ್ಲೇಷಣೆಗಳು ಮತ್ತು ಒಳನೋಟಗಳು",
        "consultant": "ಎಐ ಸಲಹೆಗಾರ",
        "settings": "ಪ್ರೊಫೈಲ್ ಸೆಟ್ಟಿಂಗ್ಗಳು",
        "logout": "ಲಾಗ್ ಔಟ್",
        "region": "ಪ್ರದೇಶ",
        "season": "ಋತು",
        "crop": "ಬೆಳೆಯ ಪ್ರಕಾರ",
        "rainfall": "ಮಳೆ (ಮಿಮೀ)",
        "temperature": "ತಾಪಮಾನ (°C)",
        "rainfall_trend": "ಹಿಂದಿನ ಮಳೆ ಪ್ರವೃತ್ತಿ (ಮಿಮೀ)",
        "borewell": "ಕೊಳವೆಬಾವಿ ಅವಲಂಬನೆ (%)",
        "analyze": "ವಿಶ್ಲೇಷಣೆ ಮತ್ತು ಮುನ್ಸೂಚನೆ",
        "system_status": "ಸಿಸ್ಟಮ್ ಸ್ಥಿತಿ",
        "api_status": "ಎಪಿಐ ಸ್ಥಿತಿ",
        "active_region": "ಸಕ್ರಿಯ ಪ್ರದೇಶ",
        "connection": "ಸಂಪರ್ಕ",
        "pro_tip": "ಪ್ರೊ ಸಲಹೆ",
        "risk_level": "ಅಪಾಯದ ಮಟ್ಟ",
        "status": "ಸ್ಥಿತಿ",
        "explanation": "ವಿಶ್ಲೇಷಣೆ",
        "recommendations": "ತಜ್ಞರ ಸಲಹೆಗಳು",
        "groundwater_forecast": "ಅಂತರ್ಜಲ ಆಳ ಮುನ್ಸೂಚನೆ",
        "rainfall_forecast": "ಮಳೆ ಮುನ್ಸೂಚನೆ",
        "temperature_forecast": "ತಾಪಮಾನ ಮುನ್ಸೂಚನೆ",
        "risk_distribution": "ಅಪಾಯ ವಿತರಣೆ ವಿಶ್ಲೇಷಣೆ",
        "ask_btn": "ತಜ್ಞರ ಸಲಹೆ ಪಡೆಯಿರಿ",
        "quick_questions": "ತ್ವರಿತ ಪ್ರಶ್ನೆಗಳು",
        "ask_anything": "ಬೆಳೆ ನಿರ್ವಹಣೆ, ಜಲ ಸಂರಕ್ಷಣೆ, ಅಥವಾ ಕೃಷಿ ಪದ್ಧತಿಗಳ ಬಗ್ಗೆ ಕೇಳಿ:",
        "current_water_level": "ಪ್ರಸ್ತುತ ನೀರಿನ ಮಟ್ಟ",
        "current_temp": "ಪ್ರಸ್ತುತ ತಾಪಮಾನ",
        "below_ground": "ನೆಲದ ಕೆಳಗೆ",
        "air_temperature": "ಗಾಳಿಯ ತಾಪಮಾನ",
        "online": "ಆನ್‌ಲೈನ್",
        "secure": "ಸುರಕ್ಷಿತ",
        "analysis_complete": "ವಿಶ್ಲೇಷಣೆ ಪೂರ್ಣವಾಯಿತು! ವಿವರವಾದ ಚಾರ್ಟ್‌ಗಳಿಗಾಗಿ ವಿಶ್ಲೇಷಣೆಗಳನ್ನು ಪರಿಶೀಲಿಸಿ.",
        "no_data": "ಯಾವುದೇ ಡೇಟಾ ಕಂಡುಬಂದಿಲ್ಲ. ದಯವಿಟ್ಟು ಮೊದಲು ಹೋಮ್ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್‌ನಲ್ಲಿ ವಿಶ್ಲೇಷಣೆ ರನ್ ಮಾಡಿ.",
        "preferences_updated": "ಆದ್ಯತೆಗಳನ್ನು ನವೀಕರಿಸಲಾಗಿದೆ!",
        "password_updated": "ಪಾಸ್‌ವರ್ಡ್ ನವೀಕರಿಸಲಾಗಿದೆ!",
        "save_preferences": "ಆದ್ಯತೆಗಳನ್ನು ಉಳಿಸಿ",
        "favorite_region": "ಮೆಚ್ಚಿನ ಪ್ರದೇಶ",
        "regional_preferences": "ಪ್ರಾದೇಶಿಕ ಆದ್ಯತೆಗಳು",
        "security": "ಭದ್ರತೆ",
        "current_password": "ಪ್ರಸ್ತುತ ಪಾಸ್‌ವರ್ಡ್",
        "new_password": "ಹೊಸ ಪಾಸ್‌ವರ್ಡ್",
        "update_password": "ಪಾಸ್‌ವರ್ಡ್ ಅಪ್‌ಡೇಟ್ ಮಾಡಿ",
        "login": "ಲಾಗಿನ್",
        "signup": "ಸೈನ್ ಅಪ್",
        "username": "ಬಳಕೆದಾರಹೆಸರು",
        "email": "ಇಮೇಲ್",
        "password": "ಪಾಸ್‌ವರ್ಡ್",
        "access_dashboard": "ಡ್ಯಾಶ್‌ಬೋರ್ಡ್ ಪ್ರವೇಶಿಸಿ",
        "create_account": "ಖಾತೆ ರಚಿಸಿ"
    },
    "Telugu": {
        "app_title": "అక్వాగార్డ్ ఏఐ",
        "tagline": "స్మార్ట్ భూగర్భజల నిర్వహణ వ్యవస్థ",
        "welcome": "స్వాగతం",
        "dashboard": "హోమ్ డ్యాష్‌బోర్డ్",
        "analytics": "విశ్లేషణలు",
        "consultant": "ఏఐ సలహాదారు",
        "settings": "ప్రొఫైల్ సెట్టింగులు",
        "logout": "లాగౌట్",
        "region": "ప్రాంతం",
        "season": "సీజన్",
        "crop": "పంట రకం",
        "rainfall": "వర్షపాతం (మిమీ)",
        "temperature": "ఉష్ణోగ్రత (°C)",
        "rainfall_trend": "గత వర్షపాతం (మిమీ)",
        "borewell": "బోరువెల్ ఆధారపడటం (%)",
        "analyze": "విశ్లేషణ & అంచనా",
        "ask_btn": "నిపుణుల సలహా పొందండి",
        "quick_questions": "త్వరిత ప్రశ్నలు",
        "ask_anything": "వ్యవసాయం, నీటి పరిరక్షణ, లేదా పంటల గురించి అడగండి:",
        "current_water_level": "ప్రస్తుత నీటి మట్టం",
        "current_temp": "ప్రస్తుత ఉష్ణోగ్రత",
        "below_ground": "నేల క్రింద",
        "air_temperature": "గాలి ఉష్ణోగ్రత",
        "online": "ఆన్‌లైన్",
        "secure": "సురక్షితం",
        "risk_level": "ప్రమాద స్థాయి",
        "status": "స్థితి",
        "recommendations": "నిపుణుల సలహాలు",
        "groundwater_forecast": "భూగర్భ జలాల అంచనా",
        "rainfall_forecast": "వర్షపాతం అంచనా",
        "temperature_forecast": "ఉష్ణోగ్రత అంచనా",
        "risk_distribution": "ప్రమాద పంపిణీ విశ్లేషణ"
    },
    "Tamil": {
        "app_title": "அக்வாகார்ட் ஏஐ",
        "tagline": "ஸ்மார்ட் நிலத்தடி நீர் மேலாண்மை அமைப்பு",
        "welcome": "வரவேற்கிறோம்",
        "dashboard": "முகப்பு டாஷ்போர்டு",
        "analytics": "பகுப்பாய்வுகள்",
        "consultant": "ஏஐ ஆலோசகர்",
        "settings": "சுயவிவர அமைப்புகள்",
        "logout": "வெளியேறு",
        "region": "பகுதி",
        "season": "பருவம்",
        "crop": "பயிர் வகை",
        "rainfall": "மழைப்பொழிவு (மிமீ)",
        "temperature": "வெப்பநிலை (°C)",
        "rainfall_trend": "முந்தைய மழைப் போக்கு (மிமீ)",
        "borewell": "போர்வெல் சார்பு (%)",
        "analyze": "பகுப்பாய்வு & கணிப்பு",
        "ask_btn": "நிபுணர் ஆலோசனை பெறுக",
        "quick_questions": "விரைவான கேள்விகள்",
        "ask_anything": "விவசாயம், நீர் பாதுகாப்பு, அல்லது பயிர்கள் பற்றி கேளுங்கள்:",
        "current_water_level": "தற்போதைய நீர் மட்டம்",
        "current_temp": "தற்போதைய வெப்பநிலை",
        "below_ground": "நிலத்தின் கீழ்",
        "air_temperature": "காற்று வெப்பநிலை",
        "online": "இணையத்தில்",
        "secure": "பாதுகாப்பானது",
        "risk_level": "ஆபத்து நிலை",
        "status": "நிலை",
        "recommendations": "நிபுணர் பரிந்துரைகள்",
        "groundwater_forecast": "நிலத்தடி நீர் முன்கணிப்பு",
        "rainfall_forecast": "மழைப்பொழிவு முன்கணிப்பு",
        "temperature_forecast": "வெப்பநிலை முன்கணிப்பு",
        "risk_distribution": "ஆபத்து விநியோக பகுப்பாய்வு"
    },
    "Marathi": {
        "app_title": "अक्वागार्ड एआय",
        "tagline": "स्मार्ट भूजल व्यवस्थापन प्रणाली",
        "welcome": "स्वागत आहे",
        "dashboard": "मुख्य डॅशबोर्ड",
        "analytics": "विश्लेषणे",
        "consultant": "एआय सल्लागार",
        "settings": "प्रोफाइल सेटिंग्ज",
        "logout": "लॉगआउट",
        "region": "प्रदेश",
        "season": "हंगाम",
        "crop": "पीक प्रकार",
        "rainfall": "पाऊस (मिमी)",
        "temperature": "तापमान (°C)",
        "rainfall_trend": "मागील पाऊस (मिमी)",
        "borewell": "बोअरवेल अवलंबित्व (%)",
        "analyze": "विश्लेषण आणि अंदाज",
        "ask_btn": "तज्ञ सल्ला घ्या",
        "quick_questions": "त्वरित प्रश्न",
        "ask_anything": "शेती, जलसंधारण, किंवा पिकांबद्दल विचारा:",
        "current_water_level": "सध्याची पाणी पातळी",
        "current_temp": "सध्याचे तापमान",
        "below_ground": "जमिनीखाली",
        "air_temperature": "हवेचे तापमान",
        "online": "ऑनलाइन",
        "secure": "सुरक्षित",
        "risk_level": "जोखीम पातळी",
        "status": "स्थिती",
        "recommendations": "तज्ञ शिफारसी",
        "groundwater_forecast": "भूजल खोली अंदाज",
        "rainfall_forecast": "पाऊस अंदाज",
        "temperature_forecast": "तापमान अंदाज",
        "risk_distribution": "जोखीम वितरण विश्लेषण"
    }
}

REGIONS_LIST = sorted(list(REGION_TRANSLATIONS["English"].keys()))
CROPS_LIST = sorted(list(CROP_TRANSLATIONS["English"].keys()))

# =========================================================================
# LOGIN
# =========================================================================
if not st.session_state["token"]:
    st.markdown(f"<div class='typing-title'>{t('app_title')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='subtitle'>{t('tagline')}</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        tab_login, tab_signup = st.tabs([f"🔒 {t('login')}", f"✍️ {t('signup')}"])
        
        with tab_login:
            l_user = st.text_input(t("username"), key="l_user")
            l_pass = st.text_input(t("password"), type="password", key="l_pass")
            if st.button(t("access_dashboard"), use_container_width=True):
                if l_user and l_pass:
                    try:
                        res = requests.post(f"{API_URL}/auth/login", json={"username": l_user, "password": l_pass})
                        if res.status_code == 200:
                            data = res.json()
                            st.session_state["token"] = data["token"]
                            st.session_state["username"] = l_user
                            st.session_state["pref_region"] = data.get("pref_region") or "Kolar"
                            st.rerun()
                        else:
                            st.error("Invalid credentials")
                    except Exception as e:
                        st.error(f"Connection error: {e}")
        
        with tab_signup:
            s_user = st.text_input(t("username"), key="su")
            s_email = st.text_input(t("email"))
            s_pass = st.text_input(t("password"), type="password", key="sp")
            if st.button(t("create_account"), use_container_width=True):
                if s_user and s_pass and s_email:
                    try:
                        res = requests.post(f"{API_URL}/auth/signup", json={"username": s_user, "email": s_email, "password": s_pass})
                        if res.status_code == 200:
                            st.success(t("account_created"))
                        else:
                            st.error(t("signup_failed"))
                    except Exception as e:
                        st.error(f"Connection error: {e}")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# =========================================================================
# SIDEBAR
# =========================================================================
with st.sidebar:
    st.markdown(f"### 👋 {t('welcome')}, **{st.session_state['username']}**")
    st.markdown("---")
    
    selected = option_menu(
        None,
        [t("dashboard"), t("analytics"), t("consultant"), t("settings"), t("logout")],
        icons=['house', 'graph-up', 'robot', 'gear', 'box-arrow-right'],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#00f2fe", "font-size": "18px"},
            "nav-link": {"font-size": "14px", "text-align": "left", "margin": "0px", "color": "white"},
            "nav-link-selected": {"background-color": "rgba(0, 242, 254, 0.2)", "border-radius": "8px"},
        }
    )
    
    st.markdown("---")
    st.session_state["lang"] = st.selectbox("🌐 Language", ["English", "Hindi", "Kannada", "Telugu", "Tamil", "Marathi"])
    st.markdown("---")
    st.caption("© 2024 AquaGuard AI")

if selected == t("logout"):
    st.session_state["token"] = None
    st.session_state["username"] = None
    st.session_state["pred_results"] = None
    st.rerun()

# =========================================================================
# DASHBOARD
# =========================================================================
if selected == t("dashboard"):
    st.markdown(f"<div class='typing-title' style='font-size:2rem;'>📊 {t('dashboard')}</div>", unsafe_allow_html=True)
    
    col_input, col_info = st.columns([2, 1])
    
    with col_input:
        with st.form("input_form"):
            st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
            st.subheader("📝 Input Parameters")
            
            region = st.selectbox(t("region"), REGIONS_LIST, format_func=localize_region,
                index=REGIONS_LIST.index(st.session_state["pref_region"]) if st.session_state["pref_region"] in REGIONS_LIST else 0)
            season = st.selectbox(t("season"), ["Winter", "Summer", "Monsoon", "Post_Monsoon"], format_func=localize_season)
            crop = st.selectbox(t("crop"), CROPS_LIST, format_func=localize_crop)
            
            col1, col2 = st.columns(2)
            with col1:
                rainfall = st.slider(t("rainfall"), 0, 500, 120)
                temp = st.slider(t("temperature"), 10.0, 50.0, 28.0)
            with col2:
                rainfall_trend = st.slider(t("rainfall_trend"), 0, 500, 150)
                borewell = st.slider(t("borewell"), 0, 100, 60)
            
            submit = st.form_submit_button(t("analyze"), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    with col_info:
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        st.markdown(f"### ℹ️ {t('system_status')}")
        st.markdown(f"**🟢 {t('api_status')}:** {t('online')}")
        st.markdown(f"**🌍 {t('active_region')}:** {localize_region(region)}")
        st.markdown(f"**🔒 {t('connection')}:** {t('secure')}")
        st.markdown("---")
        st.info(f"💡 **{t('pro_tip')}:** {t('analysis_complete')}")
        st.markdown("</div>", unsafe_allow_html=True)

    if submit:
        payload = {
            "region": region, "season": season, "crop_type": crop,
            "rainfall_mm": rainfall, "rainfall_trend_mm": rainfall_trend,
            "temperature_c": temp, "borewell_dependency": borewell
        }
        with st.spinner("🔄 Analyzing data..."):
            try:
                res = requests.post(f"{API_URL}/predict", json=payload, headers=HEADERS).json()
                recs = requests.post(f"{API_URL}/recommend", json=payload, headers=HEADERS).json()
                forecast = requests.post(f"{API_URL}/forecast", json=payload, headers=HEADERS).json()
                alert = requests.post(f"{API_URL}/alert", json=payload, headers=HEADERS).json()
                
                st.session_state["pred_results"] = {
                    "payload": payload,
                    "risk": res.get("risk", "Safe"),
                    "risk_score": res.get("risk_score", 0),
                    "status": res.get("status", "Normal"),
                    "explanation": res.get("explanation", ""),
                    "crop_suitability": res.get("crop_suitability", {}),
                    "recommendations": recs.get("recommendations", []),
                    "forecasts": forecast.get("forecasts", {}),
                    "alert": alert.get("alert", False),
                    "alert_msg": alert.get("message", "")
                }
                st.success(f"✅ {t('analysis_complete')}")
            except Exception as e:
                st.error(f"Error: {e}")

# =========================================================================
# ANALYTICS & INSIGHTS (With PDF Button at the bottom)
# =========================================================================
if selected == t("analytics"):
    st.markdown(f"<div class='typing-title' style='font-size:2rem;'>📈 {t('analytics')}</div>", unsafe_allow_html=True)
    
    data = st.session_state.get("pred_results")
    if not data:
        st.warning(f"⚠️ {t('no_data')}")
    else:
        if data.get("alert", False):
            st.error(f"🚨 {data.get('alert_msg', 'Alert!')}")
        
        # Risk metrics row
        col1, col2, col3, col4 = st.columns(4)
        risk_class = f"risk-{data['risk'].lower()}"
        
        with col1:
            st.markdown(f"<div class='metric-card'><h4>{t('risk_level')}</h4><div class='{risk_class}'>{localize_status(data['risk'])}</div><small>Score: {data.get('risk_score', 0)}%</small></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='metric-card'><h4>{t('status')}</h4><div style='font-size:1rem'>{data['status'][:40]}</div></div>", unsafe_allow_html=True)
        with col3:
            gw_val = data['forecasts'].get('groundwater', {}).get('1_month', 45)
            st.markdown(f"<div class='metric-card'><h4>💧 {t('current_water_level')}</h4><div style='font-size:24px'>{gw_val}m</div><small>{t('below_ground')}</small></div>", unsafe_allow_html=True)
        with col4:
            temp_val = data['payload']['temperature_c']
            st.markdown(f"<div class='metric-card'><h4>🌡️ {t('current_temp')}</h4><div style='font-size:24px'>{temp_val}°C</div><small>{t('air_temperature')}</small></div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Charts Row
        col_ch1, col_ch2, col_ch3 = st.columns(3)
        
        with col_ch1:
            st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
            st.subheader(f"💧 {t('groundwater_forecast')}")
            gw = data['forecasts'].get('groundwater', {})
            fig_gw = go.Figure(data=[
                go.Bar(x=['1 Month', '3 Months', '1 Year'],
                       y=[gw.get('1_month', 45), gw.get('3_months', 52), gw.get('1_year', 60)],
                       marker_color=['#00f2fe', '#4facfe', '#10b981'],
                       text=[f"{gw.get('1_month', 45)}m", f"{gw.get('3_months', 52)}m", f"{gw.get('1_year', 60)}m"],
                       textposition='outside')
            ])
            fig_gw.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                                 font=dict(color='white'), height=350, showlegend=False,
                                 yaxis_title="Depth (meters)")
            st.plotly_chart(fig_gw, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col_ch2:
            st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
            st.subheader(f"🌧️ {t('rainfall_forecast')}")
            rf = data['forecasts'].get('rainfall', {})
            fig_rf = go.Figure(data=[
                go.Scatter(x=['1 Month', '3 Months', '1 Year'],
                          y=[rf.get('1_month', 85), rf.get('3_months', 72), rf.get('1_year', 58)],
                          mode='lines+markers',
                          line=dict(color='#00f2fe', width=3),
                          marker=dict(size=12, color='#4facfe'),
                          fill='tozeroy',
                          fillcolor='rgba(0, 242, 254, 0.2)')
            ])
            fig_rf.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                                 font=dict(color='white'), height=350, showlegend=False,
                                 yaxis_title="Rainfall (mm)")
            st.plotly_chart(fig_rf, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col_ch3:
            st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
            st.subheader(f"🌡️ {t('temperature_forecast')}")
            tmp = data['forecasts'].get('temperature', {})
            fig_tmp = go.Figure(data=[
                go.Bar(x=['1 Month', '3 Months', '1 Year'],
                       y=[tmp.get('1_month', 28), tmp.get('3_months', 31), tmp.get('1_year', 33)],
                       marker_color=['#f59e0b', '#ef4444', '#10b981'],
                       text=[f"{tmp.get('1_month', 28)}°C", f"{tmp.get('3_months', 31)}°C", f"{tmp.get('1_year', 33)}°C"],
                       textposition='outside')
            ])
            fig_tmp.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                                 font=dict(color='white'), height=350, showlegend=False,
                                 yaxis_title="Temperature (°C)")
            st.plotly_chart(fig_tmp, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Pie Chart and Recommendations
        col_pie, col_rec = st.columns(2)
        
        with col_pie:
            st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
            st.subheader(f"📊 {t('risk_distribution')}")
            
            risk_dist = {
                localize_pie_label('Water Scarcity'): data.get('risk_score', 30),
                localize_pie_label('Temperature Stress'): max(0, min(30, (data['payload']['temperature_c'] - 25) * 3)) if data['payload']['temperature_c'] > 25 else 10,
                localize_pie_label('Crop Demand'): 25 if data['payload']['crop_type'] in ['Rice', 'Sugarcane'] else 15,
                localize_pie_label('Normal'): max(10, 100 - data.get('risk_score', 30))
            }
            
            fig_pie = go.Figure(data=[go.Pie(labels=list(risk_dist.keys()), values=list(risk_dist.values()),
                                            hole=0.4, 
                                            marker=dict(colors=['#ef4444', '#f59e0b', '#00f2fe', '#10b981']),
                                            textinfo='percent', textposition='auto')])
            fig_pie.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                                 font=dict(color='white'), height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col_rec:
            st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
            st.subheader(f"💡 {t('recommendations')}")
            localized_recs = get_localized_recommendations(data['risk'])
            for rec in localized_recs:
                st.info(rec)
            st.markdown("</div>", unsafe_allow_html=True)
        
        # ===== PDF DOWNLOAD BUTTON ADDED HERE =====
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_pdf1, col_pdf2, col_pdf3 = st.columns([1, 2, 1])
        with col_pdf2:
            if st.button("📥 Download PDF Report", use_container_width=True):
                with st.spinner("Generating PDF..."):
                    pdf_file = generate_pdf_report(data, st.session_state["lang"])
                    with open(pdf_file, "rb") as f:
                        st.download_button(
                            label="📄 Click to Save PDF",
                            data=f,
                            file_name=pdf_file,
                            mime="application/pdf",
                            use_container_width=True
                        )

# =========================================================================
# AI CONSULTANT
# =========================================================================
if selected == t("consultant"):
    st.markdown(f"<div class='typing-title' style='font-size:2rem;'>🤖 {t('consultant')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='subtitle'>{t('tagline')}</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
    
    st.markdown(f"### 💡 {t('quick_questions')}")
    q_cols = st.columns(4)
    questions = [
        "🌧️ " + ("Rainfall management" if st.session_state["lang"] == "English" else "वर्षा प्रबंधन" if st.session_state["lang"] == "Hindi" else "ಮಳೆ ನಿರ್ವಹಣೆ"),
        "🌾 " + ("Best crops for dry regions" if st.session_state["lang"] == "English" else "सूखे क्षेत्रों के लिए सर्वोत्तम फसलें" if st.session_state["lang"] == "Hindi" else "ಬರಗಾಲ ಪ್ರದೇಶಗಳಿಗೆ ಉತ್ತಮ ಬೆಳೆಗಳು"),
        "💧 " + ("Water conservation tips" if st.session_state["lang"] == "English" else "जल संरक्षण टिप्स" if st.session_state["lang"] == "Hindi" else "ನೀರು ಸಂರಕ್ಷಣಾ ಸಲಹೆಗಳು"),
        "🌡️ " + ("Temperature effects" if st.session_state["lang"] == "English" else "तापमान प्रभाव" if st.session_state["lang"] == "Hindi" else "ತಾಪಮಾನ ಪರಿಣಾಮಗಳು")
    ]
    
    for i, (col, q) in enumerate(zip(q_cols, questions)):
        with col:
            if st.button(q, use_container_width=True):
                st.session_state["ai_question"] = q
    
    st.markdown("---")
    
    default_q = st.session_state.get("ai_question", "")
    user_question = st.text_area(t("ask_anything"), value=default_q, height=100)
    
    if st.button(t("ask_btn"), use_container_width=True):
        if user_question:
            with st.spinner("🤔 Consulting AI expert..."):
                ai_response = get_ai_response(user_question, st.session_state["lang"])
                st.markdown(f"<div style='background: rgba(0, 242, 254, 0.1); border-radius: 12px; padding: 1rem; margin-top: 1rem; border-left: 4px solid #00f2fe;'><strong>🤖 AquaGuard AI:</strong><br><br>{ai_response}</div>", unsafe_allow_html=True)
        else:
            st.warning("Please enter your question.")
    
    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================================
# SETTINGS
# =========================================================================
if selected == t("settings"):
    st.markdown(f"<div class='typing-title' style='font-size:2rem;'>⚙️ {t('settings')}</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        st.subheader(f"📍 {t('regional_preferences')}")
        new_pref = st.selectbox(t("favorite_region"), REGIONS_LIST, format_func=localize_region,
            index=REGIONS_LIST.index(st.session_state["pref_region"]) if st.session_state["pref_region"] in REGIONS_LIST else 0)
        if st.button(t("save_preferences"), use_container_width=True):
            try:
                res = requests.post(f"{API_URL}/auth/update-pref", 
                                   json={"username": st.session_state["username"], "pref_region": new_pref}, 
                                   headers=HEADERS)
                if res.status_code == 200:
                    st.session_state["pref_region"] = new_pref
                    st.success(t("preferences_updated"))
                else:
                    st.error("Update failed")
            except Exception as e:
                st.error(f"Error: {e}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        st.subheader(f"🔐 {t('security')}")
        old_p = st.text_input(t("current_password"), type="password")
        new_p = st.text_input(t("new_password"), type="password")
        if st.button(t("update_password"), use_container_width=True):
            if old_p and new_p and len(new_p) >= 6:
                try:
                    res = requests.post(f"{API_URL}/auth/update-password", 
                                       json={"username": st.session_state["username"], "old_password": old_p, "new_password": new_p}, 
                                       headers=HEADERS)
                    if res.status_code == 200:
                        st.success(t("password_updated"))
                    else:
                        st.error("Update failed")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Password must be at least 6 characters")
        st.markdown("</div>", unsafe_allow_html=True)