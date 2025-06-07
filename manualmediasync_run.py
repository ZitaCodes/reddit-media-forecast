import subprocess
import json
from datetime import datetime
import os
import praw

# Initialize Reddit
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

    # Save to file
    with open("media_forecast_output.json", "w") as f:
        json.dump(forecast, f, indent=2)

    print("\n✅ Media Forecast written to media_forecast_output.json")

    # Log summaries
    print("\n🎬 Reddit Media Sync Matches This Week:")
    for i, item in enumerate(forecast["media_forecast"], 1):
        print(f"{i}. [{item['subreddit']}] {item['title']} (score: {item['score']})")

    # Full JSON
    print("\n🧾 Full JSON for GitHub:")
    print(json.dumps(forecast, indent=2))
