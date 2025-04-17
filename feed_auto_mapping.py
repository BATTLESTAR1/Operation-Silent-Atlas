import requests
import folium
from folium.plugins import MarkerCluster, HeatMap
from geopy.geocoders import Nominatim
from datetime import datetime
import time
import json

API_KEY = #your api key

# Define threat terms
threat_keywords = ["weapons", "soldiers","army", "attack", "explosion", "ambush", "drone", "militant", "gun", "killed", "the", "border", "security", "movement", "incident"]

# Define hotzones
hotzones = {
    "Northern Sinai": ["Rafah", "El Arish", "Sheikh Zuweid", "Bir al-Abd"],
    "Gaza Strip": ["Gaza City", "Khan Yunis", "Beit Hanoun"],
    "Southern Israel": ["Eilat", "Beersheba", "Kerem Shalom"],
    "Red Sea Corridor": ["Bab el-Mandeb", "Hodeidah", "Aden", "Djibouti"],
    "Western Sahel": ["Mali", "Burkina Faso", "Niger", "Niamey", "Timbuktu"],
}

# Country context for better geocoding
region_countries = {
    "Northern Sinai": "Egypt",
    "Gaza Strip": "Palestine",
    "Southern Israel": "Israel",
    "Red Sea Corridor": "Yemen",
    "Western Sahel": "Mali"
}

# Base map
m = folium.Map(location=[28.5, 35.2], zoom_start=5)
geolocator = Nominatim(user_agent="intel-dashboard")

# Clusters and heatmap data
marker_cluster = MarkerCluster().add_to(m)
heat_data = []
# Log container
threat_log = []

# Threat summary counters
summary = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}

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

    try:
        response = requests.get("https://newsapi.org/v2/everything", params=params)
        articles = response.json().get("articles", [])
        print(f"\n🔎 Region: {region} | Locations: {locations}")
        print(f"📰 Found {len(articles)} articles")

        threat_detected = False

        for article in articles:
            title = article['title']
            description = article.get('description') or ""
            content = f"{title} {description}".lower()
            threat_score = sum(1 for k in threat_keywords if k in content)
            threat_level = "HIGH" if threat_score >= 3 else "MEDIUM" if threat_score == 2 else "LOW" if threat_score == 1 else "NONE"
            print(f"→ Checking: {title}")
            print(f"→ Threat Score: {threat_score}") #Check if article are being returned from api

            if threat_level != "NONE":
                location_match = next((loc for loc in locations if loc.lower() in content), None)
                if location_match:
                    try:
                        country = region_countries.get(region, "")
                        geo = geolocator.geocode(f"{location_match}, {country}")
                        if geo:
                            # Marker
                            threat_detected = True
                            popup_html = f"""
                            <b>{region}</b><br>
                            <b>Threat:</b> {threat_level}<br>
                            <b>Headline:</b> {title}<br>
                            <a href="{article['url']}" target="_blank">Read more</a>
                            """
                            folium.Marker(
                                location=[geo.latitude, geo.longitude],
                                popup=folium.Popup(popup_html, max_width=300),
                                icon=folium.Icon(color="red" if threat_score >= 3 else "orange" if threat_score == 2 else "green")
                            ).add_to(marker_cluster)

                            # Add to heatmap (weighted)
                            heat_data.append([geo.latitude, geo.longitude, threat_score])

                            summary[threat_level] += 1
                            print(f"📍 {region} → {title} [{threat_level}]")
                            time.sleep(1)
                            import json

                            # Inside the article-processing loop (right after confirming `geo`):
                            threat_log.append({
                                "region": region,
                                "location": location_match,
                                "title": title,
                                "threat_level": threat_level,
                                "threat_score": threat_score,
                                "coordinates": [geo.latitude, geo.longitude],
                                "source_url": article['url'],
                                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
                            })

                    except Exception as e:
                        print(f"⚠️ Geolocation error for {location_match}: {e}")
    except Exception as e:
        print(f"❌ API error for {region}: {e}")
if not threat_detected:
    try:
        fallback_location = geolocator.geocode(locations[0] + ", " + region_countries.get(region, ""))
        if fallback_location:
            folium.Marker(
                location=[fallback_location.latitude, fallback_location.longitude],
                popup=f"{region}: No current threats detected",
                icon=folium.Icon(color="gray", icon="info-sign")
            ).add_to(marker_cluster)
            print(f"🟢 {region} → No current threats detected.")
            time.sleep(1)
    except Exception as e:
        print(f"⚠️ Fallback location error for {region}: {e}")

# 🔥 Add heatmap layer
if heat_data:
    HeatMap(heat_data, radius=15, blur=10, max_zoom=7).add_to(m)

# 📊 Summary panel
summary_text = f"""
Threat Summary:<br>
🟥 HIGH: {summary['HIGH']}<br>
🟧 MEDIUM: {summary['MEDIUM']}<br>
🟩 LOW: {summary['LOW']}<br>
"""

timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

summary_html = f"""
<div style="position: fixed;
            bottom: 50px; left: 50px; width: 170px; height: 170px;
            z-index:9999; font-size:14px;
            background-color: white;
            border:2px solid grey;
            padding: 10px;">
<b>🕒 Last Updated:</b><br>{timestamp}<br><br>{summary_text}
</div>
"""
# Log container
threat_log = []

m.get_root().html.add_child(folium.Element(summary_html))

# Save threat log to file
with open("threat_log.json", "w") as f:
    json.dump(threat_log, f, indent=4)

print("🗂️ Threat logs saved: 'threat_log.json'")

# 💾 Save map
m.save("global_threat_dashboard.html")
print("\n✅ Tactical Heatmap Ready: 'global_threat_dashboard.html'")
