# run_preprocessing.py
import pandas as pd
from src.components.preprocessor import ReviewPreprocessor  # your class

def run(df: pd.DataFrame = None):
    """
    Run preprocessing either on a provided DataFrame or from CSV paths in config.
    Returns processed DataFrame.
    """
    preprocessor = ReviewPreprocessor()

    if df is not None:
        # Use the provided DataFrame instead of reading CSV
        preprocessor.df = df
        preprocessor.stats['original_count'] = len(df)
        print(f"Processing passed DataFrame with {len(df)} rows")

        preprocessor.handle_missing_values()
        preprocessor.normalize_dates()
        preprocessor.clean_text()
        preprocessor.validate_ratings()
        preprocessor.prepare_final_output()
        return preprocessor.df
    else:
        # Process CSV file using paths from YAML config
        return preprocessor.process()


if __name__ == "__main__":
    # Run preprocessing from CSV in config
    df_processed = run()
    print(df_processed.head())
