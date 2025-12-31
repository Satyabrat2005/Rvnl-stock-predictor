import pandas as pd
import numpy as np

# Edge-based position sizing

def edge_risk_fraction(df, dt, max_risk=0.02):
    """
    Risk fraction based on EMA edge strength
    """
    if 'ema_fast' not in df.columns or 'ema_slow' not in df.columns:
        return max_risk

    edge = (df.loc[dt, 'ema_fast'] - df.loc[dt, 'ema_slow']) / df.loc[dt, 'ema_slow']
    edge = max(0.0, min(edge, 0.05))  # cap extreme values
    return (edge / 0.05) * max_risk


# -----------------------------------
# Portfolio Backtester
# -----------------------------------
class PortfolioBacktest:
    def __init__(
        self,
        data_dict,
        signals_dict,
        weights=None,
        initial_capital=100000,
        slippage=0.0005,
        commission=0.0
    ):
        self.data = data_dict
        self.signals = signals_dict
        self.weights = weights or {t: 1 / len(data_dict) for t in data_dict}
        self.initial_capital = initial_capital
        self.slippage = slippage
        self.commission = commission

        # Align all tickers on common timeline
        self.master_index = pd.Index(
            sorted(set().union(*(df.index for df in self.data.values())))
        )

        for t in self.data:
            self.data[t] = self.data[t].reindex(self.master_index, method='ffill')
            self.signals[t] = (
                self.signals[t]
                .reindex(self.master_index)
                .fillna(0)
            )

    # -----------------------------------
    def run(self):
        portfolio_cash = self.initial_capital
        equity_curve = pd.Series(index=self.master_index, dtype=float)

        trades = {t: [] for t in self.data}
        positions = {t: 0 for t in self.data}
        shares = {t: 0.0 for t in self.data}

        for dt in self.master_index:
            portfolio_value = 0.0

            for t, df in self.data.items():
                price = df.loc[dt, 'Close']
                sig = self.signals[t].loc[dt]
                prev_sig = (
                    self.signals[t].shift(1).loc[dt]
                    if dt != self.master_index[0]
                    else 0
                )

                # ---------------- BUY ----------------
                if sig == 1 and prev_sig == 0 and positions[t] == 0:
                    risk_frac = edge_risk_fraction(df, dt)
                    cash_alloc = portfolio_cash * risk_frac * self.weights[t]

                    if cash_alloc > 0:
                        entry_price = price * (1 + self.slippage)
                        shares[t] = cash_alloc / entry_price
                        cost = shares[t] * entry_price + self.commission

                        portfolio_cash -= cost
                        positions[t] = 1

                        stop_price = entry_price - 2.5 * df.loc[dt, 'atr']

                        trades[t].append({
                            'entry_time': dt,
                            'entry_price': entry_price,
                            'shares': shares[t],
                            'stop': stop_price,
                            'exit_time': None,
                            'exit_price': None,
                            'proceeds': None,
                            'exit_reason': None
                        })

                # ---------------- EXIT: SIGNAL ----------------
                elif sig == 0 and prev_sig == 1 and positions[t] == 1:
                    exit_price = price * (1 - self.slippage)
                    proceeds = shares[t] * exit_price - self.commission

                    portfolio_cash += proceeds
                    positions[t] = 0
                    shares[t] = 0

                    trades[t][-1].update({
                        'exit_time': dt,
                        'exit_price': exit_price,
                        'proceeds': proceeds,
                        'exit_reason': 'SIGNAL'
                    })

                # ---------------- EXIT: ATR STOP ----------------
                if positions[t] == 1:
                    stop = trades[t][-1]['stop']
                    if price < stop:
                        exit_price = price * (1 - self.slippage)
                        proceeds = shares[t] * exit_price - self.commission

                        portfolio_cash += proceeds
                        positions[t] = 0
                        shares[t] = 0

                        trades[t][-1].update({
                            'exit_time': dt,
                            'exit_price': exit_price,
                            'proceeds': proceeds,
                            'exit_reason': 'ATR_STOP'
                        })

                # Mark-to-market
                portfolio_value += shares[t] * price

            equity_curve.loc[dt] = portfolio_cash + portfolio_value # type: ignore

        return equity_curve, trades

    # -----------------------------------
    def compute_metrics(self, equity_curve):
        returns = equity_curve.pct_change().fillna(0)

        total_return = equity_curve.iloc[-1] / equity_curve.iloc[0] - 1
        ann_return = (1 + total_return) ** (252 / len(equity_curve)) - 1
        ann_vol = returns.std() * np.sqrt(252)
        sharpe = ann_return / ann_vol if ann_vol > 0 else np.nan

        drawdown = (equity_curve.cummax() - equity_curve) / equity_curve.cummax()
        max_dd = drawdown.max()

        return {
            'total_return': total_return,
            'annualized_return': ann_return,
            'annualized_vol': ann_vol,
            'sharpe': sharpe,
            'max_drawdown': max_dd
        }
