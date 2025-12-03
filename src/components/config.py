# ====================================================
# config.py - Configuration Settings
# ====================================================

import os
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class AnalysisConfig:
    """Configuration for the analysis pipeline"""
    
    # File paths
    INPUT_FILE: str = 'bank_reviews.csv'
    OUTPUT_FILE: str = 'analyzed_reviews.csv'
    THEME_MAPPING_FILE: str = 'theme_keywords.json'
    VISUALIZATION_DIR: str = 'visualizations'
    
    # NLP Settings
    SPACY_MODEL: str = 'en_core_web_sm'
    MIN_REVIEW_LENGTH: int = 10
    BATCH_SIZE: int = 1000
    
    # Theme Settings
    MIN_THEME_KEYWORDS: int = 3
    MAX_THEMES_PER_REVIEW: int = 2
    MAX_KEYWORDS_PER_THEME: int = 20
    
    # Sentiment thresholds
    POSITIVE_THRESHOLD: float = 0.1
    NEGATIVE_THRESHOLD: float = -0.1
    
    # Keyword extraction
    TFIDF_MAX_FEATURES: int = 100
    TFIDF_MIN_DF: int = 2
    TFIDF_MAX_DF: float = 0.9
    
    # Banking-specific stop words
    BANKING_STOP_WORDS: List[str] = None
    
    def __post_init__(self):
        if self.BANKING_STOP_WORDS is None:
            self.BANKING_STOP_WORDS = [
                'bank', 'banks', 'banking', 'account', 'accounts',
                'money', 'would', 'like', 'get', 'use', 'also',
                'really', 'one', 'even', 'much', 'many', 'well'
            ]
    
    def ensure_directories(self):
        """Create necessary directories"""
        os.makedirs(self.VISUALIZATION_DIR, exist_ok=True)
        return self


class ThemePatterns:
    """Pre-defined theme patterns for banking domain"""
    
    PATTERNS: Dict[str, List[str]] = {
        'UI_UX_DESIGN': [
            r'app', r'ui', r'ux', r'interface', r'design',
            r'user friendly', r'easy to use', r'intuitive',
            r'navigation', r'layout', r'dashboard', r'menu',
            r'color', r'font', r'appearance', r'visual'
        ],
        'RELIABILITY_PERFORMANCE': [
            r'crash', r'bug', r'glitch', r'freeze', r'hang',
            r'slow', r'lag', r'loading', r'response time',
            r'reliable', r'stable', r'performance', r'speed',
            r'downtime', r'offline', r'error', r'not working'
        ],
        'ACCOUNT_SECURITY': [
            r'login', r'password', r'security', r'authentication',
            r'biometric', r'face id', r'fingerprint', r'pin',
            r'locked', r'hacked', r'fraud', r'privacy',
            r'two factor', r'verification', r'access'
        ],
        'TRANSACTION_FEATURES': [
            r'transfer', r'payment', r'bill pay', r'deposit',
            r'withdrawal', r'atm', r'wire', r'mobile check',
            r'instant', r'pending', r'failed transaction',
            r'recurring', r'scheduled', r'auto pay'
        ],
        'CUSTOMER_SUPPORT': [
            r'support', r'customer service', r'help', r'assistance',
            r'call center', r'chat', r'email support', r'phone',
            r'wait time', r'response', r'agent', r'representative',
            r'complaint', r'issue resolution', r'feedback'
        ],
        'FEES_CHARGES': [
            r'fee', r'charge', r'cost', r'overdraft',
            r'monthly fee', r'atm fee', r'transaction fee',
            r'hidden fee', r'service charge', r'penalty',
            r'interest', r'rate', r'apr'
        ],
        'MOBILE_BANKING': [
            r'mobile', r'app', r'iphone', r'android',
            r'notification', r'push', r'alerts', r'mobile deposit',
            r'qr code', r'face id', r'touch id', r'mobile wallet'
        ]
    }