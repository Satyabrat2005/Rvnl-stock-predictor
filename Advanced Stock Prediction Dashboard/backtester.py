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
        self.data = data_dict
        self.signals = signals_dict
        self.weights = weights or {t: 1/len(data_dict) for t in data_dict}
        self.initial_capital = initial_capital
        self.slippage = slippage
        self.commission = commission

        # Align all tickers to a master index (union of dates)
        self.master_index = pd.Index(sorted(set().union(*(df.index for df in self.data.values()))))
        for t in self.data:
            self.data[t] = self.data[t].reindex(self.master_index, method='ffill')
            self.signals[t] = self.signals[t].reindex(self.master_index, method='ffill').fillna(0)
