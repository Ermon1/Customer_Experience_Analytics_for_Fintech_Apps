# ====================================================
# keyword_extractor.py - Keyword Extraction
# ====================================================

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import Dict, List, Tuple, Any
import pandas as pd
from collections import Counter
from config import AnalysisConfig


class KeywordExtractor:
    """Extracts keywords using TF-IDF"""
    
    def __init__(self, config: AnalysisConfig):
        self.config = config
        self.tfidf_vectorizer = None
        self.keyword_scores = {}
    
    def extract_with_tfidf(self, texts: List[str], 
                          max_keywords: int = None) -> Dict[str, Dict[str, float]]:
        """Extract keywords using TF-IDF"""
        if max_keywords is None:
            max_keywords = self.config.TFIDF_MAX_FEATURES
        
        # Initialize TF-IDF
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=max_keywords,
            stop_words='english',
            ngram_range=(1, 3),
            min_df=self.config.TFIDF_MIN_DF,
            max_df=self.config.TFIDF_MAX_DF,
            token_pattern=r'(?u)\b[a-zA-Z]{3,}\b'
        )
        
        # Fit and transform
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
        feature_names = self.tfidf_vectorizer.get_feature_names_out()
        
        # Calculate average TF-IDF scores
        avg_scores = np.array(tfidf_matrix.mean(axis=0)).flatten()
        
        # Calculate frequencies
        frequencies = np.array((tfidf_matrix > 0).sum(axis=0)).flatten()
        
        # Create keyword dictionary
        keywords = {}
        for idx, (feature, score, freq) in enumerate(zip(feature_names, avg_scores, frequencies)):
            keywords[feature] = {
                'tfidf_score': float(score),
                'frequency': int(freq),
                'avg_tfidf': float(score)
            }
        
        # Sort by TF-IDF score
        sorted_keywords = dict(sorted(
            keywords.items(), 
            key=lambda x: x[1]['tfidf_score'], 
            reverse=True
        ))
        
        self.keyword_scores = sorted_keywords
        return sorted_keywords
    
    def get_top_keywords(self, n: int = 20) -> List[Tuple[str, float]]:
        """Get top N keywords by TF-IDF score"""
        if not self.keyword_scores:
            return []
        
        sorted_items = sorted(
            self.keyword_scores.items(),
            key=lambda x: x[1]['tfidf_score'],
            reverse=True
        )[:n]
        
        return [(kw, data['tfidf_score']) for kw, data in sorted_items]
    
    def extract_from_dataframe(self, df: pd.DataFrame, 
                              text_column: str = 'lemmatized_text') -> Dict[str, Dict[str, float]]:
        """Extract keywords from dataframe column"""
        print("🔑 Extracting keywords with TF-IDF...")
        
        texts = df[text_column].tolist()
        keywords = self.extract_with_tfidf(texts)
        
        # Display top keywords
        top_keywords = self.get_top_keywords(15)
        print("✅ Top 15 Keywords:")
        for i, (kw, score) in enumerate(top_keywords, 1):
            print(f"   {i:2d}. {kw:25s} (score: {score:.4f})")
        
        return keywords