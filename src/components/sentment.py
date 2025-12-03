# ====================================================
# sentiment_analyzer.py - Sentiment Analysis
# ====================================================

from textblob import TextBlob
from typing import Dict, List, Tuple
import pandas as pd
from config import AnalysisConfig


class SentimentAnalyzer:
    """Performs sentiment analysis on reviews"""
    
    def __init__(self, config: AnalysisConfig):
        self.config = config
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of a single text"""
        if not text or len(text.strip()) < 10:
            return {
                'sentiment_label': 'neutral',
                'sentiment_score': 0.0,
                'sentiment_confidence': 0.0,
                'subjectivity': 0.0
            }
        
        analysis = TextBlob(text)
        polarity = analysis.sentiment.polarity
        subjectivity = analysis.sentiment.subjectivity
        
        # Classify sentiment
        if polarity > self.config.POSITIVE_THRESHOLD:
            label = 'positive'
        elif polarity < self.config.NEGATIVE_THRESHOLD:
            label = 'negative'
        else:
            label = 'neutral'
        
        # Calculate confidence (based on distance from neutral)
        confidence = min(abs(polarity) * 2, 1.0)
        
        return {
            'sentiment_label': label,
            'sentiment_score': round(polarity, 4),
            'sentiment_confidence': round(confidence, 4),
            'subjectivity': round(subjectivity, 4)
        }
    
    def analyze_batch(self, texts: List[str]) -> List[Dict[str, float]]:
        """Analyze sentiment for a batch of texts"""
        results = []
        
        for text in texts:
            results.append(self.analyze_sentiment(text))
        
        return results
    
    def analyze_dataframe(self, df: pd.DataFrame, 
                         text_column: str = 'review_text') -> pd.DataFrame:
        """Add sentiment analysis to dataframe"""
        print("😊 Analyzing sentiment...")
        
        result_df = df.copy()
        sentiment_results = []
        
        # Process in batches
        for i in range(0, len(result_df), self.config.BATCH_SIZE):
            batch_texts = result_df[text_column].iloc[i:i + self.config.BATCH_SIZE].tolist()
            batch_results = self.analyze_batch(batch_texts)
            sentiment_results.extend(batch_results)
        
        # Add sentiment columns to dataframe
        for col in ['sentiment_label', 'sentiment_score', 
                   'sentiment_confidence', 'subjectivity']:
            result_df[col] = [r[col] for r in sentiment_results]
        
        # Add sentiment summary
        sentiment_counts = result_df['sentiment_label'].value_counts()
        print(f"✅ Sentiment analysis complete:")
        for label, count in sentiment_counts.items():
            percentage = (count / len(result_df)) * 100
            print(f"   {label.upper():8s}: {count} reviews ({percentage:.1f}%)")
        
        return result_df