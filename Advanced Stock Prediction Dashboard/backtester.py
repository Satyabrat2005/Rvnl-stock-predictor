import pandas as pd
import numpy as np

class PortfolioBacktest:
    def __init__(self, data_dict, signals_dict, weights=None, initial_capital=100000, slippage=0.0005, commission=0.0):
        """
        Multi-asset portfolio backtester.

        Args:
            data_dict (dict): {ticker: price_df}
            signals_dict (dict): {ticker: signal_series}
            weights (dict): {ticker: weight} (sum to 1)
            initial_capital (float): starting portfolio cash
            slippage (float): fraction slippage on trades
            commission (float): flat commission per trade
        """
