import pandas as pd
import numpy as np

def ema(series, span):
    return series.ewm(span=span, adjust=False).mean()

def rsi(series, length=14):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ma_up = up.ewm(alpha=1/length, adjust=False).mean()
    ma_down = down.ewm(alpha=1/length, adjust=False).mean()
    rs = ma_up / (ma_down + 1e-12)
    return 100 - (100/(1+rs))

def rolling_volatility(series, window=20):
    returns = series.pct_change()
    return returns.rolling(window).std() * np.sqrt(252)

def macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return macd_line, signal_line, hist

def bollinger_bands(series, window=20, n_std=2):
    sma = series.rolling(window).mean()
    std = series.rolling(window).std()
    upper = sma + n_std*std
    lower = sma - n_std*std
    return upper, lower

def atr(df, window=14):
    high_low = df['High'] - df['Low']
    high_close = (df['High'] - df['Close'].shift()).abs()
    low_close = (df['Low'] - df['Close'].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(window).mean()

#Feature preparation
def prepare_features(
    df,
    fast_ema=20,
    slow_ema=50,
    rsi_len=14,
    vol_window=20,
    compute_macd=True,
    compute_bb=True,
    compute_atr=True
):
    df = df.copy()
    df['Close'] = df['Adj_Close']

    # Basic indicators
    df['ema_fast'] = ema(df['Close'], fast_ema)
    df['ema_slow'] = ema(df['Close'], slow_ema)
    df['rsi'] = rsi(df['Close'], rsi_len)
    df['vol'] = rolling_volatility(df['Close'], vol_window)

    # Optional advanced indicators
    if compute_macd:
        df['macd'], df['macd_signal'], df['macd_hist'] = macd(df['Close'])
    if compute_bb:
        df['bb_upper'], df['bb_lower'] = bollinger_bands(df['Close'])
    if compute_atr:
        df['atr'] = atr(df)
