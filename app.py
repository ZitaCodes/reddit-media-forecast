import json
from reddit_media_scraper import get_reddit_forecast

def main():
    print("🔍 Starting Reddit Media Forecast scraper...")
    try:
        forecast_data = get_reddit_forecast()
        with open("media_forecast_output.json", "w") as f:
            json.dump(forecast_data, f, indent=4)
        print(f"✅ Successfully wrote {len(forecast_data)} entries to media_forecast_output.json.")
    except Exception as e:
        print(f"❌ Error during forecast scraping: {e}")

if __name__ == "__main__":
    main()
