import streamlit as st
import folium
from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium
import requests
import time
from datetime import datetime

# Config
API_KEY = ""  # Replace with your NewsAPI key
geolocator = Nominatim(user_agent="intel-live-feed")
threat_keywords = ["attack", "explosion", "ambush", "drone", "militant", "shelling"]

# Hotzones
hotzones = {
    "Northern Sinai": ["Rafah", "El Arish", "Sheikh Zuweid", "Bir al-Abd"],
    "Gaza Strip": ["Gaza City", "Khan Yunis"],
    "Red Sea": ["Bab el-Mandeb", "Hodeidah", "Aden"],
}

# Enhanced Mock Pin Injection with Fallbacks
mock_threats = [
    {
        "region": "Northern Sinai",
        "name": "Militant movement near checkpoint",
        "level": "MEDIUM",
        "fallback_coords": [31.1318, 33.7984],
    },
    {
        "region": "Red Sea",
        "name": "Pirate signal on radar",
        "level": "HIGH",
        "fallback_coords": [12.6320, 43.4025],
    },
    {
        "region": "Gaza Strip",
        "name": "Tunnel activity reported",
        "level": "MEDIUM",
        "fallback_coords": [31.3403, 34.3032],
    },
]

# UI
st.set_page_config(page_title="Global Threat Dashboard", layout="wide")
st.title("🛰️ Global Threat Intelligence Dashboard")
st.markdown("**Live Feed Active | Simulated Pins Enabled | Threat Level Mapping Operational**")

map_center = [28.5, 34.2]
m = folium.Map(location=map_center, zoom_start=5)
marker_cluster = MarkerCluster().add_to(m)

# Mock Pin Injection (🟠 Test Data for Visual Coverage)
for mock in mock_threats:
    try:
        geo = geolocator.geocode(mock["region"], timeout=10)
        if geo:
            location = [geo.latitude, geo.longitude]
        else:
            location = mock["fallback_coords"]
            st.warning(f"⚠️ Fallback used for {mock['region']}")
    except Exception as e:
        location = mock["fallback_coords"]
        st.error(f"⚠️ Geocoding error for {mock['region']}: {e}. Using fallback.")

    folium.Marker(
        location=location,
        popup=f"🟠 MOCK | {mock['name']} | Threat: {mock['level']}",
        icon=folium.Icon(color="orange" if mock["level"] == "MEDIUM" else "red"),
    ).add_to(marker_cluster)

    time.sleep(1.5)  # Respect geocoder rate limit

# 🔴 LIVE THREAT FEED LOOP
for region, locations in hotzones.items():
    query = " OR ".join(locations)
    params = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 5,
        "apiKey": API_KEY
    }

    response = requests.get("https://newsapi.org/v2/everything", params=params)
    articles = response.json().get("articles", [])

    st.subheader(f"📍 {region} — {len(articles)} Articles")

    for article in articles:
        title = article["title"]
        desc = article.get("description") or ""
        content = f"{title} {desc}".lower()

        threat_score = sum(1 for k in threat_keywords if k in content)
        threat_level = (
            "HIGH" if threat_score >= 3 else
            "MEDIUM" if threat_score == 2 else
            "LOW" if threat_score == 1 else
            None
        )

        location_match = next((loc for loc in locations if loc.lower() in content), None)

        if location_match and threat_level:
            try:
                geo = geolocator.geocode(location_match, timeout=10)
                if geo:
                    folium.Marker(
                        location=[geo.latitude, geo.longitude],
                        popup=f"{title} | Threat: {threat_level.upper()}",
                        icon=folium.Icon(color="red" if threat_level == "HIGH" else "orange" if threat_level == "MEDIUM" else "green")
                    ).add_to(marker_cluster)
                    time.sleep(1)
            except Exception as e:
                st.warning(f"Live Geolocation failed for {location_match}")

# Render map
st_folium(m, width=1400, height=700)

# Footer
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
