import requests
import folium
from geopy.geocoders import Nominatim
import time

API_KEY = ""

# Define threat terms
threat_keywords = ["attack", "explosion", "ambush", "drone", "militant", "shelling", "smuggling"]

# Define hotzones
hotzones = {
    "Northern Sinai": ["Rafah", "El Arish", "Sheikh Zuweid", "Bir al-Abd"],
    "Gaza Strip": ["Gaza City", "Khan Yunis", "Beit Hanoun"],
    "Southern Israel": ["Eilat", "Beersheba", "Kerem Shalom"],
    "Red Sea Corridor": ["Bab el-Mandeb", "Hodeidah", "Aden", "Djibouti"],
    "Western Sahel": ["Mali", "Burkina Faso", "Niger", "Niamey", "Timbuktu"],
}

# 🌍 Base map centered near Middle East
m = folium.Map(location=[28.5, 35.2], zoom_start=5)
geolocator = Nominatim(user_agent="intel-dashboard")

print("\n📡 SCANNING MULTIPLE HOTZONES...\n")

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

    for article in articles:
        title = article['title']
        description = article.get('description') or ""
        content = f"{title} {description}".lower()
        threat_score = sum(1 for k in threat_keywords if k in content)
        threat_level = "HIGH" if threat_score >= 3 else "MEDIUM" if threat_score == 2 else "LOW" if threat_score == 1 else "NONE"

        location_match = next((loc for loc in locations if loc.lower() in content), None)
        if location_match and threat_score > 0:
            try:
                geo = geolocator.geocode(location_match + ", Egypt" if "Sinai" in region else location_match)
                if geo:
                    folium.Marker(
                        location=[geo.latitude, geo.longitude],
                        popup=f"{region}: {title}\nThreat: {threat_level}",
                        icon=folium.Icon(color="red" if threat_score >= 3 else "orange" if threat_score == 2 else "green")
                    ).add_to(m)
                    print(f"📍 {region} → {title} [{threat_level}]")
                    time.sleep(1)
            except Exception as e:
                print(f"⚠️ Geolocation error: {e}")

# Save updated map
m.save("global_threat_dashboard.html")
print("\n✅ Multi-Zone Map Ready: 'global_threat_dashboard.html'")
