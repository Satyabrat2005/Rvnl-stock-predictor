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

    ema_fast = df['ema_fast']
    ema_slow = df['ema_slow']

    cross_up = (ema_fast > ema_slow) & (ema_fast.shift(1) <= ema_slow.shift(1))
    cross_down = (ema_fast < ema_slow) & (ema_fast.shift(1) >= ema_slow.shift(1))

    # Adaptive volatility threshold
    vol_thresh = df['vol'].rolling(252).quantile(vol_quantile)

    position = 0
    for t in df.index:
        if position == 0:
            if (
                cross_up.loc[t]
                and df.loc[t, 'rsi'] < rsi_high
                and df.loc[t, 'vol'] < vol_thresh.loc[t]
            ):
                position = 1

        elif position == 1:
            if (
                cross_down.loc[t]
                or df.loc[t, 'rsi'] > rsi_high
                or df.loc[t, 'vol'] > vol_thresh.loc[t]
            ):
                position = 0

        s.loc[t] = position

    # Apply cooldown (IMPORTANT)
    s = apply_cooldown(s, cooldown_days=5)
    return s

# Bollinger Mean Reversion
def bollinger_signals(df, lookback=20):
    """
    Buy when price crosses below lower band,
    exit when price reverts to mid-band
    """
    s = pd.Series(index=df.index, dtype=float)
    s[:] = 0.0

    position = 0
    for t in df.index:
        price = df.loc[t, 'Close']
        lower = df.loc[t, 'bb_lower']
        upper = df.loc[t, 'bb_upper']
        mid = (upper + lower) / 2

        if position == 0 and price < lower:
            position = 1
        elif position == 1 and price > mid:
            position = 0

        s.loc[t] = position

    # Mean reversion → shorter cooldown
    s = apply_cooldown(s, cooldown_days=3)
    return s

# MACD Trend Following
def macd_signals(df):
    """
    MACD trend-following with stability filter
    """
    s = pd.Series(index=df.index, dtype=float)
    s[:] = 0.0

    macd = df['macd']
    signal = df['macd_signal']

    cross_up = (macd > signal) & (macd.shift(1) <= signal.shift(1))
    cross_down = (macd < signal) & (macd.shift(1) >= signal.shift(1))

    position = 0
    for t in df.index:
