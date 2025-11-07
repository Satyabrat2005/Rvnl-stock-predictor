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
                if 'open' in lc: col_map[col] = 'Open'
                elif 'high' in lc: col_map[col] = 'High'
                elif 'low' in lc: col_map[col] = 'Low'
                elif 'close' in lc and 'adj' not in lc: col_map[col] = 'Close'
                elif 'adj' in lc and 'close' in lc: col_map[col] = 'Adj_Close'
                elif 'volume' in lc: col_map[col] = 'Volume'
            df.rename(columns=col_map, inplace=True) # type: ignore

            # Ensure all required columns exist
            for c in ['Open','High','Low','Close','Adj_Close','Volume']:
                if c not in df.columns: # type: ignore
                    df[c] = df['Close'] # type: ignore
                  
