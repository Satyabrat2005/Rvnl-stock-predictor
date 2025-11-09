import pandas as pd
import numpy as np

# --- Basic indicators ---
def ema(series, span):
    return series.ewm(span=span, adjust=False).mean()
