from tabulate import tabulate

# 🔍 Step 1: Define threat keywords
threat_keywords = {
    "explosion": 3,
    "attack": 3,
    "militants": 2,
    "weapons": 2,
    "IED": 3,
    "troops": 1,
    "ambush": 3,
    "convoy": 2,
    "border": 1,
    "smuggling": 2
}

# 🛰️ Step 2: Mock intelligence feed
intel_feed = [
    "Unusual convoy movement spotted south of El Arish.",
    "Explosion reported near Sheikh Zuweid. Casualties unknown.",
    "Israeli drones observed monitoring border near Rafah.",
    "No unusual activity near Taba crossing.",
    "Checkpoint attack suspected west of Bir al-Abed.",
    "IED defused along route to military base near Al-Joura."
]

# 🛠️ Step 3: Analyze feed
results = []

for report in intel_feed:
    risk_score = 0
    hits = []
    for keyword, score in threat_keywords.items():
        if keyword.lower() in report.lower():
            risk_score += score
            hits.append(keyword)

    results.append({
        "Report": report,
        "Keywords Found": ", ".join(hits) if hits else "None",
        "Risk Score": risk_score
    })

# 📊 Step 4: Display Dashboard
print("\n📍 Northern Sinai Protective Intel Dashboard:\n")
print(tabulate(results, headers="keys", tablefmt="fancy_grid"))
