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
