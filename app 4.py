
import streamlit as st
import math
import requests
import pandas as pd

st.set_page_config(page_title="Address-Based Snowmaking Tracker", layout="centered")
st.title("📍 Address-Based Snowmaking Tracker")

# Wet-bulb temp using Stull's approximation
def calculate_wetbulb(T, RH):
    Tw = T * math.atan(0.151977 * (RH + 8.313659)**0.5) +          math.atan(T + RH) - math.atan(RH - 1.676331) +          0.00391838 * RH**1.5 * math.atan(0.023101 * RH) - 4.686035
    return round(Tw, 2)

# Get coordinates from address using OpenStreetMap
def geocode_address(address):
    response = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": address, "format": "json"}
    )
    data = response.json()
    if not data:
        return None
    return float(data[0]["lat"]), float(data[0]["lon"]), data[0]["display_name"]

# User input
address = st.text_input("Enter your address or town:", value="Simsbury, CT")

if address:
    coords = geocode_address(address)
    if coords:
        lat, lon, place_name = coords
        st.markdown(f"**📍 Location found:** {place_name}")

        # Fetch hourly weather
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "temperature_2m,relative_humidity_2m",
            "temperature_unit": "fahrenheit",
            "timezone": "auto"
        }
        weather = requests.get("https://api.open-meteo.com/v1/forecast", params=params).json()
        temps = weather["hourly"]["temperature_2m"]
        humidity = weather["hourly"]["relative_humidity_2m"]
        times = weather["hourly"]["time"]

        wetbulbs = [calculate_wetbulb(t, h) for t, h in zip(temps, humidity)]
        df = pd.DataFrame({
            "Time": pd.to_datetime(times),
            "Air Temp (°F)": temps,
            "Humidity (%)": humidity,
            "Wet-Bulb (°F)": wetbulbs,
            "Snowmaking Score": [max(0, 27 - w) for w in wetbulbs]  # Lower wetbulb = better
        })

        st.metric("Current Wet-Bulb Temp", f"{wetbulbs[0]} °F")
        st.metric("Snowmaking Condition", "✅ YES" if wetbulbs[0] <= 27 else "🔴 NO")

        # Plot bar chart
        st.subheader("🕒 Hour-by-Hour Snowmaking Quality")
        st.bar_chart(data=df.set_index("Time")["Snowmaking Score"])
    else:
        st.error("Address not found. Try a different one.")
