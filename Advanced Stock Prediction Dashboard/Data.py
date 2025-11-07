import yfinance as yf
import pandas as pd

def fetch_price_data(tickers, start, end):
  all_data = {}
    for ticker in tickers:
        try:
            df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=False)
            if df.empty: # type: ignore
                print(f"No data for {ticker}, skipping...")
                continue

            # Flatten columns if MultiIndex
            if isinstance(df.columns, pd.MultiIndex): # type: ignore
                df.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in df.columns] # type: ignore

            # Standardize columns
            col_map = {}
            for col in df.columns: # type: ignore
                lc = col.lower()

