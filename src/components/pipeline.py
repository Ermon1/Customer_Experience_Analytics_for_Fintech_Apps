# ====================================================
# pipeline.py - Main Pipeline Orchestrator
# ====================================================

import pandas as pd
import json
from datetime import datetime
from typing import Dict, Any
import os

from config import AnalysisConfig
from preprocessor import TextPreprocessor
from sentiment_analyzer import SentimentAnalyzer
from keyword_extractor import KeywordExtractor
from theme_clusterer import ThemeClusterer
from visualizer import ResultsVisualizer


class BankReviewPipeline:
    """Main pipeline orchestrator"""
    
    def __init__(self, config: AnalysisConfig):
        self.config = config
        self.preprocessor = TextPreprocessor(config)
        self.sentiment_analyzer = SentimentAnalyzer(config)
        self.keyword_extractor = KeywordExtractor(config)
        self.theme_clusterer = ThemeClusterer(config)
        self.visualizer = ResultsVisualizer(config)
        
        # Results storage
        self.results_df = None
        self.theme_assignments = None
        self.keywords = None
    
    def load_data(self) -> pd.DataFrame:
        """Load and validate input data"""
        print("📂 Loading data...")
        
        try:
            df = pd.read_csv(self.config.INPUT_FILE)
            
            # Validate required columns
            required_cols = ['review_id', 'review_text']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")
            
            # Clean data
            df = df.dropna(subset=['review_text'])
            df['review_text'] = df['review_text'].astype(str)
            
            # Filter very short reviews
            initial_count = len(df)
            df = df[df['review_text'].str.len() >= self.config.MIN_REVIEW_LENGTH]
            
            print(f"✅ Loaded {len(df)} reviews (filtered from {initial_count})")
            return df
            
        except FileNotFoundError:
            print(f"❌ Error: File '{self.config.INPUT_FILE}' not found")
            print("   Please ensure the CSV file exists in the current directory.")
            raise
    
    def run(self) -> pd.DataFrame:
        """Execute the complete analysis pipeline"""
        print("\n" + "=" * 60)
        print("🚀 BANK REVIEW ANALYSIS PIPELINE")
        print("=" * 60)
        
        # Step 1: Load data
        df = self.load_data()
        
        # Step 2: Preprocessing
        processed_df = self.preprocessor.preprocess_dataframe(df)
        
        # Step 3: Sentiment Analysis
        sentiment_df = self.sentiment_analyzer.analyze_dataframe(processed_df)
        
        # Step 4: Keyword Extraction
        self.keywords = self.keyword_extractor.extract_from_dataframe(sentiment_df)
        
        # Step 5: Theme Clustering
        self.theme_assignments = self.theme_clusterer.assign_keywords_to_themes(self.keywords)
        themed_df = self.theme_clusterer.apply_themes_to_dataframe(
            sentiment_df, 
            self.theme_assignments
        )
        
        # Step 6: Prepare final results
        self.results_df = self._prepare_final_results(themed_df)
        
        # Step 7: Save results
        self.save_results()
        
        # Step 8: Create visualizations
        self.visualizer.create_all_visualizations(self.results_df)
        
        # Step 9: Generate summary
        self.generate_summary()
        
        return self.results_df
    
    def _prepare_final_results(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare final results dataframe"""
        print("\n📋 Preparing final results...")
        
        # Select and reorder columns
        result_cols = ['review_id', 'review_text']
        
        # Add sentiment columns
        sentiment_cols = ['sentiment_label', 'sentiment_score', 
                         'sentiment_confidence', 'subjectivity']
        result_cols.extend(sentiment_cols)
        
        # Add theme columns
        result_cols.extend(['identified_themes', 'theme_count'])
        
        # Add bank name if exists
        if 'bank_name' in df.columns:
            result_cols.append('bank_name')
        
        # Add timestamp
        result_cols.append('processing_timestamp')
        
        # Create results dataframe
        results_df = df[result_cols].copy()
        
        # Truncate long review texts for readability
        results_df['review_text'] = results_df['review_text'].apply(
            lambda x: x[:500] + '...' if len(x) > 500 else x
        )
        
        # Add processing timestamp
        results_df['processing_timestamp'] = datetime.now().isoformat()
        
        print(f"✅ Final results prepared: {len(results_df)} reviews")
        return results_df
    
    def save_results(self):
        """Save all analysis results"""
        print("\n💾 Saving results...")
        
        # Ensure directories exist
        self.config.ensure_directories()
        
        # 1. Save main results CSV
        self.results_df.to_csv(self.config.OUTPUT_FILE, index=False)
        print(f"   Main results: {self.config.OUTPUT_FILE}")
        
        # 2. Save theme keyword mappings as JSON
        theme_data = {}
        for theme, keywords in self.theme_assignments.items():
            theme_data[theme] = [
                {
                    'keyword': kw['keyword'],
                    'tfidf_score': kw['tfidf_score'],
                    'frequency': kw['frequency']
                }
                for kw in keywords[:self.config.MAX_KEYWORDS_PER_THEME]
            ]
        
        with open(self.config.THEME_MAPPING_FILE, 'w') as f:
            json.dump(theme_data, f, indent=2)
        print(f"   Theme mappings: {self.config.THEME_MAPPING_FILE}")
        
        # 3. Save keywords as JSON
        keywords_file = 'extracted_keywords.json'
        with open(keywords_file, 'w') as f:
            json.dump(self.keywords, f, indent=2, default=str)
        print(f"   Extracted keywords: {keywords_file}")
    
    def generate_summary(self):
        """Generate analysis summary report"""
        print("\n" + "=" * 60)
        print("📈 ANALYSIS SUMMARY REPORT")
        print("=" * 60)
        
        if self.results_df is None:
            print("No results to summarize")
            return
        
        # Basic statistics
        print(f"\n📊 Basic Statistics:")
        print(f"   Total Reviews Analyzed: {len(self.results_df)}")
        print(f"   Unique Banks: {self.results_df.get('bank_name', pd.Series(['Single Bank'])).nunique()}")
        
        # Sentiment summary
        print(f"\n😊 Sentiment Summary:")
        sentiment_counts = self.results_df['sentiment_label'].value_counts()
        for label, count in sentiment_counts.items():
            percentage = (count / len(self.results_df)) * 100
            print(f"   {label.upper():8s}: {count:4d} reviews ({percentage:.1f}%)")
        
        # Theme summary
        print(f"\n🏷️  Theme Summary:")
        all_themes = []
        for themes in self.results_df['identified_themes']:
            if themes != 'general':
                all_themes.extend(themes.split(';'))
        
        if all_themes:
            theme_counts = pd.Series(all_themes).value_counts()
            print(f"   Total Themes Identified: {len(theme_counts)}")
            
            print("\n   Top 5 Themes:")
            for theme, count in theme_counts.head().items():
                percentage = (count / len(self.results_df)) * 100
                clean_theme = theme.replace('_', ' ').title()
                print(f"     {clean_theme:25s}: {count:3d} reviews ({percentage:.1f}%)")
        else:
            print("   No themes identified")
        
        # Review with most themes
        max_themes_idx = self.results_df['theme_count'].idxmax()
        max_themes_review = self.results_df.loc[max_themes_idx]
        print(f"\n📝 Most Thematic Review:")
        print(f"   Review ID: {max_themes_review['review_id']}")
        print(f"   Themes: {max_themes_review['identified_themes']}")
        print(f"   Preview: {max_themes_review['review_text'][:100]}...")
        
        print("\n" + "=" * 60)
        print("✅ PIPELINE EXECUTION COMPLETE")
        print("=" * 60)