import subprocess
import json
from datetime import datetime
import os
import praw

# Initialize Reddit API
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

def get_reddit_forecast():
    subreddits = ['television', 'netflix', 'HBO', 'movies']
    keywords = ["netflix", "amazon", "show", "season", "series", "poster", "announce", "episode", "reboot", "movie"]
    collected = []

    for sub in subreddits:
        matches = []
        try:
            for post in reddit.subreddit(sub).top(time_filter='month', limit=50):
                title = post.title
                if any(keyword in title.lower() for keyword in keywords) and post.score >= 80:
                    matches.append({
                        "title": title,
                        "subreddit": sub,
                        "trend_type": "Entertainment Pulse",
                        "description": f"Redditors are actively discussing: {title[:100]}..."
                    })
                if len(matches) >= 3:
                    break
        except Exception as e:
            print(f"⚠️ Error fetching from r/{sub}: {e}")
        
        print(f"📊 r/{sub}: scanned 50, matched {len(matches)}")
        collected.extend(matches)  # ✅ THIS LINE FIXES THE ISSUE

    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "media_forecast": collected,
        "meta": {
            "source": "Reddit API (PRAW)",
            "verified": bool(collected),
            "subreddits_scanned": subreddits,
            "total_matches": len(collected)
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
