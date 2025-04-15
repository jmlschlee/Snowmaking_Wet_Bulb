
import streamlit as st
import math
import requests

st.set_page_config(page_title="Auto-Detect Snowmaking Tracker", layout="centered")
st.title("📍 Auto-Detect Snowmaking Tracker")

# Wet-bulb temp using Stull's approximation
def calculate_wetbulb(T, RH):
    Tw = T * math.atan(0.151977 * (RH + 8.313659)**0.5) +          math.atan(T + RH) - math.atan(RH - 1.676331) +          0.00391838 * RH**1.5 * math.atan(0.023101 * RH) - 4.686035
    return round(Tw, 2)

# Try to fetch location via IP
st.markdown("Fetching your approximate location and weather data...")
location = requests.get("https://ipinfo.io/json").json()
lat, lon = map(float, location["loc"].split(","))
city = location.get("city", "")
region = location.get("region", "")

# Get weather from Open-Meteo API
params = {
    "latitude": lat,
    "longitude": lon,
    "current": ["temperature_2m", "relative_humidity_2m"],
    "timezone": "auto"
}
weather = requests.get("https://api.open-meteo.com/v1/forecast", params=params).json()
temp_f = weather["current"]["temperature_2m"]
humidity = weather["current"]["relative_humidity_2m"]

# Calculate wet-bulb temp
wetbulb = calculate_wetbulb(temp_f, humidity)

# Display
st.metric(label="Location", value=f"{city}, {region}")
st.metric(label="Air Temperature", value=f"{temp_f} °F")
st.metric(label="Humidity", value=f"{humidity}%")
st.metric(label="Wet-Bulb Temp", value=f"{wetbulb} °F")

# Evaluate snowmaking
if wetbulb <= 0:
    st.success("🌨️ Ideal snowmaking conditions! (0°F wet-bulb or lower)")
elif wetbulb <= 27:
    st.info("❄️ Marginal to good snowmaking possible (0–27°F wet-bulb)")
else:
    st.warning("🔴 Too warm for snowmaking (>27°F wet-bulb)")

st.caption("Live weather by Open-Meteo · Location via ipinfo.io · Wet-bulb calc: Stull (2011)")
