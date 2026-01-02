import yfinance as yf
import pandas as pd


def fetch_price_data(tickers, start, end
    """
    Fetch OHLCV data reliably (works better for NSE stocks than yf.download)
    """
    all_data = {}

    for ticker in tickers:
        try:
            tk = yf.Ticker(ticker)

            # history() is more reliable than download() for NSE
            df = tk.history(
                start=start,
                end=end,
                auto_adjust=False,
                actions=False
            )

            if df.empty:
                print(f"No data for {ticker}, skipping...")
                continue
