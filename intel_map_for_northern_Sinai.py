import folium

# Step 1: Map Centered on Northern Sinai
northern_sinai_map = folium.Map(location=[30.5, 33.5], zoom_start=8)

# Step 2: Sample Reports with Coordinates and Risk
reports = [
    {"location": "El Arish", "lat": 31.131, "lon": 33.798, "report": "Unusual convoy movement spotted south of El Arish.", "risk": 2},
    {"location": "Sheikh Zuweid", "lat": 31.216, "lon": 34.070, "report": "Explosion reported near Sheikh Zuweid.", "risk": 3},
    {"location": "Rafah", "lat": 31.287, "lon": 34.244, "report": "Israeli drones observed monitoring border near Rafah.", "risk": 1},
    {"location": "Taba", "lat": 29.492, "lon": 34.896, "report": "No unusual activity near Taba crossing.", "risk": 0},
    {"location": "Bir al-Abed", "lat": 31.009, "lon": 33.021, "report": "Checkpoint attack suspected west of Bir al-Abed.", "risk": 3},
    {"location": "Al-Joura", "lat": 29.785, "lon": 33.808, "report": "IED defused near Al-Joura base.", "risk": 3}
]

# Step 3: Function to Determine Marker Color
def get_color(risk_score):
    if risk_score >= 3:
        return 'red'
    elif risk_score == 2:
        return 'orange'
    elif risk_score == 1:
        return 'yellow'
    else:
        return 'green'

# Step 4: Add Markers to Map
for r in reports:
    folium.Marker(
        location=[r['lat'], r['lon']],
        popup=f"{r['location']}: {r['report']} (Risk: {r['risk']})",
        icon=folium.Icon(color=get_color(r['risk']))
    ).add_to(northern_sinai_map)

# Step 5: Save Map
northern_sinai_map.save("northern_sinai_intel_map.html")
print("✅ Map created: 'northern_sinai_intel_map.html'")
