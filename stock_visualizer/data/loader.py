# data/loader.py
import yfinance as yf
import pandas as pd


class DataLoader:
    @staticmethod
    def load_stock_data(symbol, start_date, end_date, multi_level_bool=False):
        """Load stock data from Yahoo Finance"""
        try:
            df = yf.download(
                symbol,
                start=start_date,
                end=end_date,
                multi_level_bool=multi_level_bool,
            )
            return df
        except Exception as e:
            print(f"Error loading data: {e}")
            return None

    @staticmethod
    def validate_data(df):
        """Check if dataframe has required columns"""
        required_columns = ["Open", "High", "Low", "Close", "Volume"]
        return all(col in df.columns for col in required_columns)
