import yfinance as yf
import pandas as pd

def fetch_price_data(tickers, start, end):
  all_data = {}
    for ticker in tickers:
        try:
