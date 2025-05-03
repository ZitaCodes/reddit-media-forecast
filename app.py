import subprocess
import json
from datetime import datetime
import os
import praw
from flask import Flask, jsonify, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

OUTPUT_FILE = "media_forecast_output.json"

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
            for post in reddit.subreddit(sub).top(time_filter='week', limit=50):
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

    forecast = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "media_forecast": collected,
        "meta": {
            "source": "Reddit API (PRAW)",
            "verified": bool(collected),
            "subreddits_scanned": subreddits,
            "total_matches": len(collected)
        }
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(forecast, f, indent=2)

    print(f"✅ Successfully wrote {len(collected)} entries to {OUTPUT_FILE}")
    return forecast


@app.route("/")
def root():
    if os.path.exists(OUTPUT_FILE):
        return send_file(OUTPUT_FILE, mimetype="application/json")
    return jsonify({"status": "No media forecast data available."}), 404

@app.route('/media_forecast_output.json')
def serve_forecast():
    if os.path.exists(OUTPUT_FILE):
        return send_file(OUTPUT_FILE, mimetype='application/json')
    else:
        return jsonify({"status": "No media forecast data available."}), 404


if __name__ == "__main__":
    get_reddit_forecast()
    print("🔁 Starting auto-commit and push to GitHub...")
    try:
        subprocess.run(["git", "add", OUTPUT_FILE])
        subprocess.run(["git", "commit", "-m", "📡 Auto-push: updated forecast data"], check=False)
        subprocess.run(["git", "push"])
    except Exception as e:
        print("❌ Git push failed:", e)

    # Keep server running so Render can serve output
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
