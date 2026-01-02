import yfinance as yf
import pandas as pd


def fetch_price_data(tickers, start, end
    """
    Fetch OHLCV data reliably (works better for NSE stocks than yf.download)
    """
    all_data = {}
