
import requests

# STEP 1: Insert your NewsAPI key here
API_KEY = "f7776cd2722f4a1f89167ead69038403"

# STEP 2: Define region & threat keywords
region_keywords = ["Sinai", "Rafah", "El Arish", "Sheikh Zuweid", "Egypt border"]
threat_keywords = ["attack", "explosion", "militant", "IED", "ambush", "clash", "troops", "drone", "surveillance",
                   "smuggling"]

# STEP 3: Build NewsAPI request
url = "https://newsapi.org/v2/everything"
params = {
    "q": " OR ".join(region_keywords),
    "language": "en",
    "sortBy": "publishedAt",
    "pageSize": 10,
    "apiKey": API_KEY
}

# STEP 4: Make request and analyze
response = requests.get(url, params=params)
articles = response.json().get("articles", [])

print("\n🛰️  OSINT FEED: Northern Sinai | Threat Detection\n")

for article in articles:
    title = article['title']
    description = article.get('description') or ""
    combined_text = f"{title} {description}".lower()

    threat_score = sum(1 for k in threat_keywords if k in combined_text)
    threat_level = "🟥 HIGH" if threat_score >= 3 else "🟧 MEDIUM" if threat_score == 2 else "🟨 LOW" if threat_score == 1 else "🟩 NONE"

    print(f"{threat_level} | {title}")
    if threat_score > 0:
        print(f"  🔎 {description.strip()[:100]}...\n")

