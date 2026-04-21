def get_recommendations(risk_level, crop_type, rain_trend, borewell_dep):
    """
    Rule-based recommendation engine for farmers/auth.
    Provides actionable insights based on the local groundwater health.
    """
    recommendations = []
    
    # 1. Broad risk-based tips
    if risk_level == "High":
        recommendations.append("🚨 HIGH RISK: Groundwater levels are critically low. Immediate adoption of Rainwater Harvesting (RWH) trenches is mandatory.")
        if borewell_dep > 70:
            recommendations.append("📉 Reduce borewell dependency to below 50% by relying on canal water or stored rainwater temporarily.")
            
    elif risk_level == "Moderate":
        recommendations.append("⚠️ MODERATE RISK: Monitor extraction rates. Regularize pumping hours to off-peak to save power and water pressure.")
        if borewell_dep > 80:
            recommendations.append("🚱 Borewell usage is very high. Consider building farm ponds to offset usage.")
            
    else:
        recommendations.append("✅ SAFE: Groundwater levels are stable. Continue current sustainable practices.")
        
    # 2. Crop-based tips
    high_water_crops = ["Sugarcane", "Rice"]
    if crop_type in high_water_crops and risk_level in ["High", "Moderate"]:
        recommendations.append(f"🌾 Crop Shift Advisory: Shift from {crop_type} to less water-intensive crops like Millets or Pulses for the next 2 seasons.")
    
    if risk_level in ["High", "Moderate"]:
         recommendations.append("💧 Tech Advisory: Implement Drip Irrigation to save up to 40% water instead of flood irrigation.")
         
    # 3. Rain-based tips
    if rain_trend < 100 and risk_level != "Safe":
         recommendations.append("🌧️ Rain Deficit: Due to lower recent rainfall, mulch your crops to retain soil moisture and reduce evaporation.")
         
    return recommendations
