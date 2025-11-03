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

     def run(self):
        """
        Run portfolio backtest.
        Returns:
            equity_curve (pd.Series): portfolio value over time
            trades (dict): per-ticker trade logs
        """
        portfolio_cash = self.initial_capital
        equity_curve = pd.Series(index=self.master_index, dtype=float)
        trades = {t: [] for t in self.data}
        positions = {t: 0 for t in self.data}
        shares = {t: 0 for t in self.data}

        for dt in self.master_index:
            portfolio_value = 0
            for t, df in self.data.items():
                price = df.at[dt, 'Close']
                sig = self.signals[t].at[dt]
                prev_sig = self.signals[t].shift(1).at[dt] if dt != self.master_index[0] else 0

                if sig == 1 and prev_sig == 0:
                    cash_alloc = portfolio_cash * self.weights[t]
                    shares[t] = cash_alloc / price
                    cost = shares[t]*price*(1+self.slippage) + self.commission
                    portfolio_cash -= cost
                    trades[t].append({'entry_time': dt, 'entry_price': price*(1+self.slippage), 'shares': shares[t]})
                    positions[t] = 1

                 elif sig == 0 and prev_sig == 1 and positions[t] == 1:
                    exit_price = price*(1-self.slippage)
                    proceeds = shares[t]*exit_price - self.commission
                    portfolio_cash += proceeds
                    trades[t][-1].update({'exit_time': dt, 'exit_price': exit_price, 'proceeds': proceeds})
                    shares[t] = 0
                    positions[t] = 0
