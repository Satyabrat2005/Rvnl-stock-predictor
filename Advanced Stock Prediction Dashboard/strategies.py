import pandas as pd
import numpy as np 

def apply_cooldown(signal: pd.Series, cooldown_days: int = 5):
    s = signal.copy()
    last_trade = cooldown_days
    for i in range(len(s)):
        if s.iloc[i] == 1 and i - last_trade < cooldown_days:
            s.iloc[i] = 0
        elif s.iloc[i] == 1:
            last_trade = i
    return s

#  EMA + RSI + Volatility
def ema_rsi_vol_signals(df, rsi_high=70, vol_quantile=0.6):
    """
    EMA crossover + RSI + adaptive volatility filter
    """
    s = pd.Series(index=df.index, dtype=float)
    s[:] = 0.0
