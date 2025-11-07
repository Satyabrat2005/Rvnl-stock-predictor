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
