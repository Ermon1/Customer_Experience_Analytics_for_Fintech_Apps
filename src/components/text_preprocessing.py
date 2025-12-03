# ====================================================
# preprocessor.py - Text Preprocessing
# ====================================================

import re
import pandas as pd
from typing import List, Optional
import spacy
from config import AnalysisConfig


class TextPreprocessor:
    """Handles text cleaning, tokenization, lemmatization"""
    
    def __init__(self, config: AnalysisConfig):
        self.config = config
        self.nlp = self._load_spacy_model()
    
    def _load_spacy_model(self):
        """Load spaCy model with error handling"""
        try:
            nlp = spacy.load(self.config.SPACY_MODEL, 
                           disable=['parser', 'ner'])
        except OSError:
            import subprocess
            import sys
            print(f"Downloading spaCy model: {self.config.SPACY_MODEL}")
            subprocess.run([sys.executable, "-m", "spacy", 
                          "download", self.config.SPACY_MODEL])
            nlp = spacy.load(self.config.SPACY_MODEL, 
                           disable=['parser', 'ner'])
        return nlp
    
    def clean_text(self, text: str) -> str:
        """Basic text cleaning"""
        if not isinstance(text, str):
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\?!,;:\-\'"\(\)]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def lemmatize_text(self, text: str) -> str:
        """Lemmatize text using spaCy"""
        doc = self.nlp(text)
        lemmas = []
        
        for token in doc:
            # Skip stop words and very short tokens
            if (not token.is_stop and 
                not token.is_punct and 
                len(token.text) > 2 and
                token.text.lower() not in self.config.BANKING_STOP_WORDS):
                
                # Use lemma, but keep proper nouns as-is
                if token.pos_ == 'PROPN':
                    lemmas.append(token.text)
                else:
                    lemmas.append(token.lemma_)
        
        return ' '.join(lemmas)
    
    def preprocess_batch(self, texts: List[str]) -> List[str]:
        """Process a batch of texts"""
        cleaned_texts = [self.clean_text(text) for text in texts]
        lemmatized_texts = [self.lemmatize_text(text) for text in cleaned_texts]
        return lemmatized_texts
    
    def preprocess_dataframe(self, df: pd.DataFrame, 
                           text_column: str = 'review_text') -> pd.DataFrame:
        """Preprocess an entire dataframe"""
        print("🔧 Preprocessing text data...")
        
        # Create a copy to avoid modifying original
        processed_df = df.copy()
        
        # Clean text
        processed_df['cleaned_text'] = processed_df[text_column].apply(
            lambda x: self.clean_text(str(x))
        )
        
        # Filter very short reviews
        initial_len = len(processed_df)
        processed_df = processed_df[
            processed_df['cleaned_text'].str.len() >= self.config.MIN_REVIEW_LENGTH
        ]
        
        if initial_len != len(processed_df):
            print(f"   Filtered {initial_len - len(processed_df)} short reviews")
        
        # Lemmatize in batches for memory efficiency
        print("   Lemmatizing text (this may take a moment)...")
        lemmatized_texts = []
        
        for i in range(0, len(processed_df), self.config.BATCH_SIZE):
            batch = processed_df['cleaned_text'].iloc[i:i + self.config.BATCH_SIZE].tolist()
            lemmatized_batch = [self.lemmatize_text(text) for text in batch]
            lemmatized_texts.extend(lemmatized_batch)
        
        processed_df['lemmatized_text'] = lemmatized_texts
        
        print(f"✅ Preprocessing complete: {len(processed_df)} reviews ready")
        return processed_df