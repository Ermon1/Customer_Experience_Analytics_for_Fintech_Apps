import os
import pandas as pd
import numpy as np
from datetime import datetime
import re

from src.core.configLoader import config_loader

class ReviewPreprocessor:
    """Preprocessor class that reads paths from YAML automatically"""

    def __init__(self):
        # Load paths from YAML via config_loader
        cfg = config_loader.load_config("scraping")
        paths = cfg["base_processing"]["paths"]

        self.input_path = paths["raw_reviews"]
        self.output_path = paths["processed_reviews"]
        self.df = None
        self.stats = {}

    def load_data(self):
        try:
            self.df = pd.read_csv(self.input_path)
            self.stats['original_count'] = len(self.df)
            print(f"Loaded {len(self.df)} reviews from {self.input_path}")
            return True
        except Exception as e:
            print(f"Failed to load data: {e}")
            return False

    def handle_missing_values(self):
        critical_cols = ['review_text', 'rating', 'bank_name']
        before_count = len(self.df)
        self.df = self.df.dropna(subset=critical_cols)
        removed = before_count - len(self.df)
        self.df['user_name'] = self.df.get('user_name', pd.Series()).fillna('Anonymous')
        self.df['thumbs_up'] = self.df.get('thumbs_up', pd.Series()).fillna(0)
        self.df['reply_content'] = self.df.get('reply_content', pd.Series()).fillna('')
        self.stats['rows_removed_missing'] = removed
        print(f"Removed {removed} rows with missing critical values")

    def normalize_dates(self):
        if 'review_date' in self.df.columns:
            self.df['review_date'] = pd.to_datetime(self.df['review_date'], errors='coerce').dt.date
            self.df['review_year'] = pd.to_datetime(self.df['review_date']).dt.year
            self.df['review_month'] = pd.to_datetime(self.df['review_date']).dt.month

    def clean_text(self):
        if 'review_text' in self.df.columns:
            self.df['review_text'] = self.df['review_text'].fillna('').astype(str)
            self.df['review_text'] = self.df['review_text'].apply(lambda x: re.sub(r'\s+', ' ', x).strip())
            self.df = self.df[self.df['review_text'].str.len() > 0]
            self.df['text_length'] = self.df['review_text'].str.len()

    def validate_ratings(self):
        if 'rating' in self.df.columns:
            self.df = self.df[(self.df['rating'] >= 1) & (self.df['rating'] <= 5)]

    def prepare_final_output(self):
        columns_order = [
            'review_id', 'review_text', 'rating', 'review_date',
            'review_year', 'review_month', 'bank_code', 'bank_name',
            'user_name', 'thumbs_up', 'text_length', 'source'
        ]
        self.df = self.df[[c for c in columns_order if c in self.df.columns]]
        self.df = self.df.sort_values(['bank_code', 'review_date'], ascending=[True, False])
        self.df = self.df.reset_index(drop=True)

    def save_data(self):
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        self.df.to_csv(self.output_path, index=False)
        print(f"Processed data saved to {self.output_path}")

    def process(self):
        if not self.load_data():
            return None
        self.handle_missing_values()
        self.normalize_dates()
        self.clean_text()
        self.validate_ratings()
        self.prepare_final_output()
        self.save_data()
        return self.df
