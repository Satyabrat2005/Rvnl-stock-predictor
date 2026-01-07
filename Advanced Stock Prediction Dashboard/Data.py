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

            # Standardize columns
            df.rename(columns={
                "Open": "Open",
                "High": "High",
                "Low": "Low",
                "Close": "Close",
                "Volume": "Volume"
            }, inplace=True)

            # Adjusted Close handling
            if "Adj Close" in df.columns:
                df["Adj_Close"] = df["Adj Close"]
            else:
                df["Adj_Close"] = df["Close"]

            # Ensure all required columns exist
            for c in ["Open", "High", "Low", "Close", "Adj_Close", "Volume"]:
                if c not in df.columns:
                    df[c] = df["Close"]

            # Clean index
            df.index = pd.to_datetime(df.index)

            df.sort_index(inplace=True)

            all_data[ticker] = df

        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            continue

    return all_data
