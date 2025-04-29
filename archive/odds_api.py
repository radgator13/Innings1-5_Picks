import requests
from datetime import datetime, timedelta

API_KEY = '3550559967b78da8856f5c4192697b32'

# Yesterday's date
yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')

url = f"https://api.the-odds-api.com/v4/sports/baseball_mlb/odds/?apiKey={API_KEY}&regions=us&markets=totals&oddsFormat=american"

print(f"🌐 Pulling live odds feed for yesterday: {yesterday} (even though it will not filter by date)")

response = requests.get(url)

if response.status_code != 200:
    print(f"❌ Failed to pull odds - Status Code: {response.status_code}")
    print("🌐 Response Content:", response.text)
else:
    data = response.json()
    print(f"✅ Pulled {len(data)} games from live feed!")

    found_any = False

    for game in data:
        commence_time = game.get('commence_time', '')
        if commence_time.startswith(yesterday):
            print(f"✅ Found a game from yesterday: {game.get('home_team')} vs {game.get('away_team')}")
            found_any = True

    if not found_any:
        print(f"⚠️ No games from yesterday ({yesterday}) found in live feed.")
