# ====================================================
# theme_clusterer.py - Theme Clustering
# ====================================================

import re
from typing import Dict, List, Any, Set
from collections import defaultdict, Counter
from config import AnalysisConfig, ThemePatterns


class ThemeClusterer:
    """Clusters keywords into 3-5 themes per bank"""
    
    def __init__(self, config: AnalysisConfig):
        self.config = config
        self.theme_patterns = ThemePatterns.PATTERNS
        self.theme_keywords = defaultdict(list)
        self.theme_scores = defaultdict(float)
    
    def assign_keywords_to_themes(self, keywords: Dict[str, Dict[str, float]]) -> Dict[str, List[Dict]]:
        """Assign extracted keywords to themes"""
        theme_assignments = defaultdict(list)
        
        for keyword, data in keywords.items():
            keyword_lower = keyword.lower()
            assigned = False
            
            for theme, patterns in self.theme_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, keyword_lower, re.IGNORECASE):
                        theme_assignments[theme].append({
                            'keyword': keyword,
                            'tfidf_score': data['tfidf_score'],
                            'frequency': data['frequency']
                        })
                        assigned = True
                        break
                if assigned:
                    break
            
            if not assigned:
                theme_assignments['OTHER'].append({
                    'keyword': keyword,
                    'tfidf_score': data['tfidf_score'],
                    'frequency': data['frequency']
                })
        
        # Sort keywords within each theme by TF-IDF score
        for theme in theme_assignments:
            theme_assignments[theme].sort(
                key=lambda x: x['tfidf_score'], 
                reverse=True
            )
        
        # Limit keywords per theme
        for theme in theme_assignments:
            theme_assignments[theme] = theme_assignments[theme][:self.config.MAX_KEYWORDS_PER_THEME]
        
        self.theme_keywords = theme_assignments
        return theme_assignments
    
    def identify_review_themes(self, review_text: str, 
                              theme_assignments: Dict[str, List[Dict]],
                              max_themes: int = None) -> List[str]:
        """Identify which themes apply to a specific review"""
        if max_themes is None:
            max_themes = self.config.MAX_THEMES_PER_REVIEW
        
        review_lower = review_text.lower()
        theme_scores = {}
        
        for theme, keywords in theme_assignments.items():
            if theme == 'OTHER':
                continue
                
            score = 0
            for kw_data in keywords[:20]:  # Check top 20 keywords per theme
                keyword = kw_data['keyword'].lower()
                # Use word boundaries for exact matching
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, review_lower):
                    # Score based on TF-IDF and frequency
                    score += kw_data['tfidf_score'] * np.log1p(kw_data['frequency'])
            
            if score > 0:
                theme_scores[theme] = score
        
        # Get top N themes for this review
        sorted_themes = sorted(
            theme_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:max_themes]
        
        return [theme for theme, score in sorted_themes]
    
    def apply_themes_to_dataframe(self, df: pd.DataFrame, 
                                 theme_assignments: Dict[str, List[Dict]],
                                 text_column: str = 'review_text') -> pd.DataFrame:
        """Apply theme identification to entire dataframe"""
        print("🏷️  Identifying themes for each review...")
        
        result_df = df.copy()
        themes_list = []
        
        for _, row in result_df.iterrows():
            themes = self.identify_review_themes(
                row[text_column], 
                theme_assignments
            )
            themes_list.append(';'.join(themes) if themes else 'general')
        
        result_df['identified_themes'] = themes_list
        result_df['theme_count'] = result_df['identified_themes'].apply(
            lambda x: len(x.split(';')) if x != 'general' else 0
        )
        
        # Calculate theme statistics
        all_themes = []
        for themes in result_df['identified_themes']:
            if themes != 'general':
                all_themes.extend(themes.split(';'))
        
        theme_counts = Counter(all_themes)
        print("✅ Theme identification complete:")
        
        if theme_counts:
            print("   Top Themes Found:")
            for theme, count in theme_counts.most_common(10):
                percentage = (count / len(result_df)) * 100
                print(f"     {theme.replace('_', ' ').title():25s}: {count} reviews ({percentage:.1f}%)")
        else:
            print("   No strong themes identified in reviews")
        
        return result_df