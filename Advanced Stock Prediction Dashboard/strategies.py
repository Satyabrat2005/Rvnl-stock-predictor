import pandas as pd

# EMA + RSI + Volatility
def ema_rsi_vol_signals(df, rsi_high=70, vol_thresh=0.6):
  """
  Generate long/flat signals based on EMA crossover + RSI + Volatility filter
  """
  s = pd.Series(index=df.index, dtype=float)
  s[:] = 0.0
