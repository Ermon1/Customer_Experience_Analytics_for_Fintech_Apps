import os
import time
from datetime import datetime
from pathlib import Path
from tqdm import tqdm
import pandas as pd
from google_play_scraper import app, Sort, reviews

from src.core.configLoader import config_loader
from dotenv import load_dotenv

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

# -----------------------------
# Load YAML configuration
# -----------------------------
CONFIG = config_loader.load_config("scraping")["base_processing"]

# Replace placeholders like ${CBE_APP_ID} with actual .env values
for app_code, app_info in CONFIG["apps"].items():
    env_var = app_info["app_id"].strip("${}")  # remove ${} from placeholder
    app_info["app_id"] = os.getenv(env_var, "")
    if not app_info["app_id"]:
        raise ValueError(f"Missing environment variable for {app_code}: {env_var}")

# Extract final dictionaries for scraper
APP_IDS = {k: v["app_id"] for k, v in CONFIG["apps"].items()}
APP_NAMES = {k: v["name"] for k, v in CONFIG["apps"].items()}
SCRAPING_CONFIG = CONFIG["scraping"]
DATA_PATHS = CONFIG["paths"]

# -----------------------------
# Scraper class
# -----------------------------
class PlayStoreScraper:
    """Google Play Store Review Scraper (Task 1)"""

    def __init__(self):
        self.app_ids = APP_IDS
        self.bank_names = APP_NAMES
        self.reviews_per_bank = SCRAPING_CONFIG["reviews_per_bank"]
        self.lang = SCRAPING_CONFIG["lang"]
        self.country = SCRAPING_CONFIG["country"]
        self.max_retries = SCRAPING_CONFIG["max_retries"]

    # -----------------------------
    # App metadata
    # -----------------------------
    def get_app_info(self, app_id):
        try:
            result = app(app_id, lang=self.lang, country=self.country)
            return {
                "app_id": app_id,
                "title": result.get("title", "N/A"),
                "score": result.get("score", 0),
                "ratings": result.get("ratings", 0),
                "reviews": result.get("reviews", 0),
                "installs": result.get("installs", "N/A"),
            }
        except Exception as e:
            print(f"Error getting app info for {app_id}: {e}")
            return None

    # -----------------------------
    # Scraping reviews
    # -----------------------------
    def scrape_reviews(self, app_id, count=None):
        count = count or self.reviews_per_bank
        print(f"\nScraping {count} reviews for {app_id}...")

        for attempt in range(self.max_retries):
            try:
                result, _ = reviews(
                    app_id,
                    lang=self.lang,
                    country=self.country,
                    sort=Sort.NEWEST,
                    count=count,
                    filter_score_with=None,
                )
                print(f"Successfully scraped {len(result)} reviews")
                return result
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(5)
                else:
                    print(f"Failed to scrape reviews after {self.max_retries} attempts")
                    return []

    # -----------------------------
    # Process reviews
    # -----------------------------
    def process_reviews(self, reviews_data, bank_code):
        processed = []
        for review in reviews_data:
            processed.append({
                "review_id": review.get("reviewId", ""),
                "review_text": review.get("content", ""),
                "rating": review.get("score", 0),
                "review_date": review.get("at", datetime.now()),
                "user_name": review.get("userName", "Anonymous"),
                "thumbs_up": review.get("thumbsUpCount", 0),
                "reply_content": review.get("replyContent", None),
                "bank_code": bank_code,
                "bank_name": self.bank_names[bank_code],
                "app_version": review.get("reviewCreatedVersion", "N/A"),
                "source": "Google Play",
            })
        return processed

    # -----------------------------
    # Orchestrate all banks
    # -----------------------------
    def scrape_all_banks(self):
        all_reviews = []
        app_info_list = []

        print("=" * 60)
        print("Starting Google Play Store Review Scraper")
        print("=" * 60)

        # Phase 1: Fetch app info
        print("\n[1/2] Fetching app information...")
        for bank_code, app_id in self.app_ids.items():
            print(f"\n{bank_code}: {self.bank_names[bank_code]}")
            info = self.get_app_info(app_id)
            if info:
                info["bank_code"] = bank_code
                info["bank_name"] = self.bank_names[bank_code]
                app_info_list.append(info)
                print(f"Current Rating: {info['score']}, Total Ratings: {info['ratings']}, Total Reviews: {info['reviews']}")

        # Save app info CSV
        if app_info_list:
            df_info = pd.DataFrame(app_info_list)
            Path(DATA_PATHS["raw"]).mkdir(parents=True, exist_ok=True)
            df_info.to_csv(f"{DATA_PATHS['raw']}/app_info.csv", index=False)
            print(f"App information saved to {DATA_PATHS['raw']}/app_info.csv")

        # Phase 2: Scrape reviews
        print("\n[2/2] Scraping reviews...")
        for bank_code, app_id in tqdm(self.app_ids.items(), desc="Banks"):
            reviews_data = self.scrape_reviews(app_id, self.reviews_per_bank)
            if reviews_data:
                processed = self.process_reviews(reviews_data, bank_code)
                all_reviews.extend(processed)
                print(f"Collected {len(processed)} reviews for {self.bank_names[bank_code]}")
            else:
                print(f"WARNING: No reviews collected for {self.bank_names[bank_code]}")
            time.sleep(2)

        # Phase 3: Save all reviews CSV
        if all_reviews:
            df = pd.DataFrame(all_reviews)
            Path(DATA_PATHS["raw"]).mkdir(parents=True, exist_ok=True)
            df.to_csv(DATA_PATHS["raw_reviews"], index=False)
            print(f"\nTotal reviews collected: {len(df)}")
            for bank_code in self.bank_names:
                count = len(df[df["bank_code"] == bank_code])
                print(f"  {self.bank_names[bank_code]}: {count} reviews")
            print(f"Data saved to: {DATA_PATHS['raw_reviews']}")
            return df
        else:
            print("\nERROR: No reviews were collected!")
            return pd.DataFrame()

    # -----------------------------
    # Display samples
    # -----------------------------
    def display_sample_reviews(self, df, n=3):
        print("\n" + "=" * 60)
        print("Sample Reviews")
        print("=" * 60)
        for bank_code in self.bank_names:
            bank_df = df[df["bank_code"] == bank_code]
            if not bank_df.empty:
                print(f"\n{self.bank_names[bank_code]}:")
                print("-" * 60)
                samples = bank_df.head(n)
                for idx, row in samples.iterrows():
                    print(f"\nRating: {'⭐' * row['rating']}")
                    print(f"Review: {row['review_text'][:200]}...")
                    print(f"Date: {row['review_date']}")

# -----------------------------
# Main execution
# -----------------------------
def main():
    scraper = PlayStoreScraper()
    df = scraper.scrape_all_banks()
    if not df.empty:
        scraper.display_sample_reviews(df)
    return df

if __name__ == "__main__":
    reviews_df = main()
