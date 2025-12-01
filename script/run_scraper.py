from src.components.scraper import PlayStoreScraper

scraper = PlayStoreScraper()
df = scraper.scrape_all_banks()
print(df.shape)  # Scrape and save CSV
scraper.display_sample_reviews(df, n=5)  # Print 5 sample reviews per bank
