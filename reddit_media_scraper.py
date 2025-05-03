import subprocess
import json
from datetime import datetime
import os
import requests

def get_reddit_forecast():
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; ForecastBot/1.0; +http://cloutbooks.com/contact)'}
    subreddits = ['television', 'netflix', 'HBO', 'movies', 'StreamingTV']
    collected = []

    for sub in subreddits:
        url = f"https://www.reddit.com/r/{sub}/top.json?t=week&limit=25"
        try:
            res = requests.get(url, headers=headers, timeout=10)
            # ⬇️ ADD THIS LINE RIGHT BELOW
            print(f"🔍 Raw response from r/{sub}: {res.text[:300]}")  # Add this
                       
            posts = res.json().get("data", {}).get("children", [])
            for post in posts:
                data = post["data"]
                title = data.get("title", "")
                if any(keyword in title.lower() for keyword in ["netflix", "season", "trailer", "episode", "series", "premiere"]):
                    collected.append({
                        "title": title,
                        "trend_type": "Trending Media",
                        "description": f"Redditors are actively discussing: {title[:100]}..."
                    })
                if len(collected) >= 10:
                    break
        except Exception as e:
            print(f"⚠️ Error fetching from r/{sub}: {e}")

    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "media_forecast": collected,
        "meta": {
            "source": "Reddit API",
            "verified": bool(collected)
        }
    }

if __name__ == "__main__":
    forecast = get_reddit_forecast()

    with open("media_forecast_output.json", "w") as f:
        json.dump(forecast, f, indent=2)

print("🔁 Starting auto-commit and push to GitHub...")

try:
    subprocess.run(["git", "add", "media_forecast_output.json"])
    subprocess.run(["git", "commit", "-m", "📡 Auto-push: updated forecast data"], check=False)
    subprocess.run(["git", "push"])
except Exception as e:
    print("❌ Git push failed:", e)
