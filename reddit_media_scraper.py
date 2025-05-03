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
        try:
            matches = []
            posts = reddit.subreddit(sub).top(time_filter='week', limit=50)
            for post in posts:
                title = post.title
                score = post.score or 0
                if score >= 80 and any(keyword in title.lower() for keyword in keywords):
                    matches.append({
                        "title": title,
                        "trend_type": "Entertainment Pulse",
                        "description": f"Redditors are actively discussing: {title[:100]}...",
                        "subreddit": sub,
                        "score": score
                    })
                    if len(matches) >= 3:
                        break
            print(f"📊 r/{sub}: scanned 50, matched {len(matches)}")
            collected.extend(matches)
        except Exception as e:
            print(f"⚠️ Error fetching from r/{sub}: {e}")

    # 🔎 Debug output of collected data
    print(f"\n🧾 Total entries collected: {len(collected)}")
    for i, item in enumerate(collected, 1):
        print(f"{i}. [r/{item.get('subreddit')}] {item.get('title')} (score: {item.get('score')})")

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

    print("\n🔁 Starting auto-commit and push to GitHub...")

    try:
        subprocess.run(["git", "add", "media_forecast_output.json"])
        subprocess.run(["git", "commit", "-m", "📡 Auto-push: updated forecast data"], check=False)
        subprocess.run(["git", "push"])
    except Exception as e:
        print("❌ Git push failed:", e)
