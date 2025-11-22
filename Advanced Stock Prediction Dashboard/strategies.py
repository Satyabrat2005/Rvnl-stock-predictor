import pandas as pd

# EMA + RSI + Volatility
def ema_rsi_vol_signals(df, rsi_high=70, vol_thresh=0.6):
  """
  Generate long/flat signals based on EMA crossover + RSI + Volatility filter
  """
  s = pd.Series(index=df.index, dtype=float)
  s[:] = 0.0
  ema_fast, ema_slow = df['ema_fast'], df['ema_slow']
  cross_up = (ema_fast > ema_slow) & (ema_fast.shift(1) <= ema_slow.shift(1))
  cross_down = (ema_fast < ema_slow) & (ema_fast.shift(1) >= ema_slow.shift(1))
  position = 0
    for t in df.index:
        if position == 0 and cross_up.loc[t] and df.loc[t,'rsi']<rsi_high and df.loc[t,'vol']<vol_thresh:
            position = 1
        elif position == 1 and (cross_down.loc[t] or df.loc[t,'rsi']>rsi_high or df.loc[t,'vol']>vol_thresh):
            position = 0
        s.loc[t] = position
    return s

def bollinger_signals(df, lookback=20, n_std=2):
    """
    Buy when price crosses below lower band, sell/exit when price crosses above SMA
    """
    s = pd.Series(index=df.index, dtype=float)
    s[:] = 0.0
    position = 0
    for t in df.index:
        price = df.loc[t,'Close']
        lower = df.loc[t,'bb_lower']
        upper = df.loc[t,'bb_upper']
        sma = (upper + lower)/2  # middle band approx

        if position == 0 and price < lower:
            position = 1  # buy
        elif position == 1 and price > sma:
            position = 0  # exit
        s.loc[t] = position
    return s

# MACD Trend Following
def macd_signals(df):
    """
    Buy when MACD line crosses above signal line, exit when crosses below
    """
    s = pd.Series(index=df.index, dtype=float)
    s[:] = 0.0
    macd, signal = df['macd'], df['macd_signal']
    cross_up = (macd > signal) & (macd.shift(1) <= signal.shift(1))
    cross_down = (macd < signal) & (macd.shift(1) >= signal.shift(1))
    
    position = 0
    for t in df.index:
        if position == 0 and cross_up.loc[t]:
            position = 1
        elif position == 1 and cross_down.loc[t]:
            position = 0
        s.loc[t] = position
     return s
