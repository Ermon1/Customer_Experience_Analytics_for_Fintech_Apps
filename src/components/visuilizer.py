# ====================================================
# visualizer.py - Visualization
# ====================================================

import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any
import pandas as pd
import os
from config import AnalysisConfig


class ResultsVisualizer:
    """Creates visualizations from analysis results"""
    
    def __init__(self, config: AnalysisConfig):
        self.config = config
        self.set_style()
    
    def set_style(self):
        """Set visualization style"""
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")
    
    def plot_sentiment_distribution(self, df: pd.DataFrame, 
                                   save_path: str = None):
        """Plot sentiment distribution"""
        plt.figure(figsize=(10, 6))
        
        sentiment_counts = df['sentiment_label'].value_counts()
        colors = {'positive': '#4CAF50', 'negative': '#F44336', 'neutral': '#FFC107'}
        
        bars = plt.bar(
            sentiment_counts.index, 
            sentiment_counts.values,
            color=[colors.get(s, '#2196F3') for s in sentiment_counts.index],
            edgecolor='black',
            linewidth=1.5
        )
        
        plt.title('Sentiment Distribution of Bank Reviews', 
                 fontsize=14, fontweight='bold')
        plt.xlabel('Sentiment', fontsize=12)
        plt.ylabel('Number of Reviews', fontsize=12)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{int(height)}', ha='center', va='bottom', 
                    fontweight='bold', fontsize=11)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
        else:
            plt.show()
    
    def plot_theme_distribution(self, df: pd.DataFrame, 
                               save_path: str = None):
        """Plot theme distribution"""
        # Extract themes from identified_themes column
        all_themes = []
        for themes in df['identified_themes']:
            if themes != 'general':
                all_themes.extend(themes.split(';'))
        
        theme_counts = Counter(all_themes).most_common(10)
        
        if not theme_counts:
            print("No themes to visualize")
            return
        
        themes, counts = zip(*theme_counts)
        
        # Clean theme names for display
        clean_themes = [t.replace('_', ' ').title() for t in themes]
        
        plt.figure(figsize=(12, 8))
        bars = plt.barh(clean_themes, counts, color='#2196F3', 
                       edgecolor='black', linewidth=1.5)
        
        plt.title('Top 10 Themes in Bank Reviews', 
                 fontsize=14, fontweight='bold')
        plt.xlabel('Number of Reviews', fontsize=12)
        
        # Add value labels
        for bar in bars:
            width = bar.get_width()
            plt.text(width + 0.5, bar.get_y() + bar.get_height()/2.,
                    f'{int(width)}', ha='left', va='center', 
                    fontweight='bold', fontsize=11)
        
        plt.gca().invert_yaxis()  # Highest on top
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
        else:
            plt.show()
    
    def plot_sentiment_by_theme(self, df: pd.DataFrame, 
                               save_path: str = None):
        """Plot sentiment distribution by theme"""
        # Extract themes and sentiment
        theme_sentiments = []
        
        for _, row in df.iterrows():
            sentiment = row['sentiment_label']
            themes = row['identified_themes']
            
            if themes != 'general':
                for theme in themes.split(';'):
                    theme_sentiments.append({
                        'theme': theme,
                        'sentiment': sentiment
                    })
        
        if not theme_sentiments:
            return
        
        theme_sentiment_df = pd.DataFrame(theme_sentiments)
        
        # Pivot table
        pivot_table = pd.crosstab(
            theme_sentiment_df['theme'], 
            theme_sentiment_df['sentiment']
        )
        
        # Get top 8 themes
        top_themes = pivot_table.sum(axis=1).nlargest(8).index
        pivot_table = pivot_table.loc[top_themes]
        
        # Plot
        plt.figure(figsize=(14, 8))
        pivot_table.plot(kind='bar', stacked=True, 
                        color=['#F44336', '#FFC107', '#4CAF50'],
                        edgecolor='black', linewidth=1)
        
        plt.title('Sentiment Distribution by Theme', 
                 fontsize=14, fontweight='bold')
        plt.xlabel('Theme', fontsize=12)
        plt.ylabel('Number of Reviews', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.legend(title='Sentiment')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
        else:
            plt.show()
    
    def create_all_visualizations(self, df: pd.DataFrame):
        """Create all visualizations"""
        print("📊 Creating visualizations...")
        
        self.config.ensure_directories()
        
        # 1. Sentiment Distribution
        sentiment_path = os.path.join(self.config.VISUALIZATION_DIR, 
                                     'sentiment_distribution.png')
        self.plot_sentiment_distribution(df, sentiment_path)
        
        # 2. Theme Distribution
        theme_path = os.path.join(self.config.VISUALIZATION_DIR, 
                                 'theme_distribution.png')
        self.plot_theme_distribution(df, theme_path)
        
        # 3. Sentiment by Theme
        sentiment_theme_path = os.path.join(self.config.VISUALIZATION_DIR, 
                                           'sentiment_by_theme.png')
        self.plot_sentiment_by_theme(df, sentiment_theme_path)
        
        print(f"✅ Visualizations saved to '{self.config.VISUALIZATION_DIR}/'")