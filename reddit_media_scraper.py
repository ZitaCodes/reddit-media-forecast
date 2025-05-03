import subprocess
import json
from datetime import datetime
import os
import praw

# Initialize Reddit API with environment variables
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

def get_reddit_forecast():
    subreddits = ['television', 'netflix', 'HBO', 'movies']
    collected = []

    for sub in subreddits:
        try:
            for post in reddit.subreddit(sub).top(time_filter='week', limit=25):
                title = post.title
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
            "source": "Reddit API (PRAW)",
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
