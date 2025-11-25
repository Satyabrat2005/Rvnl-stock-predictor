
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from data import fetch_price_data
from features import prepare_features
from strategies import ema_rsi_vol_signals, bollinger_signals, macd_signals
from backtester import PortfolioBacktest

# Helper functions
def cagr(equity):
    years = (equity.index[-1] - equity.index[0]).days / 365.25
    return (equity.iloc[-1] / equity.iloc[0]) ** (1 / years) - 1

def sortino_ratio(equity, risk_free=0.0):
    returns = equity.pct_change().dropna()
    downside = returns[returns < 0]
    if downside.std() == 0:
        return np.nan
    return (returns.mean() - risk_free/252) / downside.std() * np.sqrt(252)

def calmar_ratio(equity):
    total_cagr = cagr(equity)
    drawdown = (equity.cummax() - equity) / equity.cummax()
    max_dd = drawdown.max()
    return total_cagr / max_dd if max_dd > 0 else np.nan

def omega_ratio(equity, target=0.0):
    returns = equity.pct_change().dropna()
    gains = (returns - target)[returns > target].sum()
    losses = -(returns - target)[returns < target].sum()
    return gains / losses if losses != 0 else np.nan

# --- Page Setup ---
st.set_page_config(page_title="JPMQuant Pro", layout="wide")
st.title("JPMQuant — Advanced Dynamic Portfolio Backtester 🚀")

# --- Sidebar ---
with st.sidebar:
    st.header("Portfolio & Strategy Settings")
    tickers_input = st.text_input("Enter tickers (comma-separated)", "JPM,AAPL,MSFT")
    start_date = st.date_input("Start date", pd.to_datetime("2018-01-01"))
    end_date = st.date_input("End date", pd.to_datetime("2024-12-31"))

    strategy = st.selectbox("Select Strategy", ["EMA+RSI", "Bollinger Mean Reversion", "MACD Trend"])

    st.markdown("### Indicators")
    use_macd = st.checkbox("MACD", True)
    use_bb = st.checkbox("Bollinger Bands", True)
    use_atr = st.checkbox("ATR", True)

    fast_ema = st.number_input("Fast EMA", 5, 200, 20)
    slow_ema = st.number_input("Slow EMA", 10, 400, 50)
    rsi_len = st.number_input("RSI length", 5, 50, 14)
    vol_window = st.number_input("Volatility window", 5, 60, 20)
    initial_cap = st.number_input("Initial Capital (USD)", 1000.0, 1000000.0, 100000.0)

    run_bt = st.button("Run Backtest")

# --- Run Backtest ---
if run_bt:
    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
    st.write(f"Fetching data for tickers: {tickers}")

    data_dict = fetch_price_data(tickers, start_date.isoformat(), end_date.isoformat())
    valid_tickers = list(data_dict.keys())
    skipped_tickers = [t for t in tickers if t not in valid_tickers]

    if skipped_tickers:
        st.warning(f"Skipped tickers (no data): {', '.join(skipped_tickers)}")
    if not valid_tickers:
        st.error("No valid tickers with data. Backtest aborted.")
        st.stop()
    else:
        st.success(f"Fetched data for: {', '.join(valid_tickers)}")

    # --- Prepare Features ---
    features_dict = {t: prepare_features(
        df,
        fast_ema=fast_ema,
        slow_ema=slow_ema,
        rsi_len=rsi_len,
        vol_window=vol_window,
        compute_macd=use_macd,
        compute_bb=use_bb,
        compute_atr=use_atr
    ) for t, df in data_dict.items()}

    # --- Generate Signals ---
    signals_dict = {}
    for t, df in features_dict.items():
        if strategy == "EMA+RSI":
            signals_dict[t] = ema_rsi_vol_signals(df)
        elif strategy == "Bollinger Mean Reversion":
            signals_dict[t] = bollinger_signals(df)
        elif strategy == "MACD Trend":
            signals_dict[t] = macd_signals(df)

    # --- Run Portfolio Backtest ---
    pb = PortfolioBacktest(data_dict, signals_dict, initial_capital=initial_cap) # type: ignore
    eq_curve, trades = pb.run()
    metrics = pb.compute_metrics(eq_curve)

    # --- Portfolio Metrics ---
    st.subheader("Portfolio Metrics")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Total Return", f"{metrics['total_return']*100:.2f}%")
    col2.metric("Annualized Return", f"{metrics['annualized_return']*100:.2f}%")
    col3.metric("Sharpe Ratio", f"{metrics['sharpe']:.2f}")
    col4.metric("Max Drawdown", f"{metrics['max_drawdown']*100:.2f}%")
    col5.metric("CAGR", f"{cagr(eq_curve)*100:.2f}%")
    col6.metric("Calmar Ratio", f"{calmar_ratio(eq_curve):.2f}")

    # --- Interactive Equity Curve ---
    st.subheader("Portfolio Equity Curve")
    fig_eq = go.Figure()
    fig_eq.add_trace(go.Scatter(x=eq_curve.index, y=eq_curve.values,
                                mode='lines', name='Equity', line=dict(color='blue')))
    fig_eq.update_layout(title="Portfolio Equity Curve", xaxis_title="Date", yaxis_title="Equity (USD)",
                         template='plotly_white')
    st.plotly_chart(fig_eq, use_container_width=True)

    # --- Risk vs Return Dashboard ---
    st.subheader("Risk vs Return per Ticker")
    rr_data = []
    for t in valid_tickers:
        eq = (features_dict[t]['Adj_Close'] / features_dict[t]['Adj_Close'].iloc[0]) * initial_cap
        rr_data.append({
            "Ticker": t,
            "Annualized Return": cagr(eq),
            "Annualized Vol": eq.pct_change().std() * np.sqrt(252),
            "Sortino": sortino_ratio(eq)
        })
    rr_df = pd.DataFrame(rr_data)

    fig_rr = go.Figure()
    fig_rr.add_trace(go.Scatter(
        x=rr_df["Annualized Vol"],
        y=rr_df["Annualized Return"],
        mode='markers+text',
        text=rr_df["Ticker"],
        textposition="top center",
        marker=dict(size=14, color=rr_df["Sortino"], colorscale="RdYlGn", showscale=True,
                    colorbar=dict(title="Sortino"))
    ))
    fig_rr.update_layout(title="Risk vs Return", xaxis_title="Annualized Volatility",
                         yaxis_title="Annualized Return", template='plotly_white')
    st.plotly_chart(fig_rr, use_container_width=True)

    # --- Trades & Analytics per Ticker ---
    st.subheader("Trades & Price Charts")
    for t in valid_tickers:
        df_trades = trades[t]
        df_price = features_dict[t]
        if df_trades:
            df_tr = pd.DataFrame(df_trades)
            df_tr['PnL'] = df_tr['proceeds'] - df_tr['entry_price']*df_tr['shares']
            df_tr['Holding Days'] = (df_tr['exit_time'] - df_tr['entry_time']).dt.days

            st.markdown(f"### {t}")
            st.dataframe(df_tr)
            st.markdown(f"- Avg Holding Days: {df_tr['Holding Days'].mean():.1f}")
            st.markdown(f"- Avg PnL: {df_tr['PnL'].mean():.2f}")
            st.markdown(f"- Win Rate: {len(df_tr[df_tr['PnL']>0])/len(df_tr)*100:.1f}%")
            st.markdown(f"- Max Win: {df_tr['PnL'].max():.2f}, Max Loss: {df_tr['PnL'].min():.2f}")

            # --- Interactive Price Chart ---
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_price.index, y=df_price['Close'], mode='lines', name='Close', line=dict(color='blue')))
            if 'ema_fast' in df_price.columns and 'ema_slow' in df_price.columns:
                fig.add_trace(go.Scatter(x=df_price.index, y=df_price['ema_fast'], mode='lines', name='Fast EMA'))
                fig.add_trace(go.Scatter(x=df_price.index, y=df_price['ema_slow'], mode='lines', name='Slow EMA'))
            if use_bb and 'bb_upper' in df_price.columns and 'bb_lower' in df_price.columns:
                fig.add_trace(go.Scatter(x=df_price.index, y=df_price['bb_upper'], line=dict(color='grey', dash='dash'), name='BB Upper'))
                fig.add_trace(go.Scatter(x=df_price.index, y=df_price['bb_lower'], line=dict(color='grey', dash='dash'), name='BB Lower'))
            for idx, trade in df_tr.iterrows():
                fig.add_trace(go.Scatter(x=[trade['entry_time']], y=[trade['entry_price']],
                                         mode='markers', marker=dict(symbol='triangle-up', color='green', size=12),
                                         name='Entry' if idx==0 else ''))
                fig.add_trace(go.Scatter(x=[trade['exit_time']], y=[trade['exit_price']],
                                         mode='markers', marker=dict(symbol='triangle-down', color='red', size=12),
                                         name='Exit' if idx==0 else ''))
            fig.update_layout(title=f"{t} Price & Trades", xaxis_title="Date", yaxis_title="Price", template='plotly_white')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"No trades for {t}")

    # --- Export Option ---
    st.subheader("Export Data")
    if st.button("Download Trades & Equity Curve Excel"):
        export_data = {f"{t}_trades": pd.DataFrame(trades[t]) for t in valid_tickers}
        export_data['portfolio_equity'] = eq_curve # type: ignore
        with pd.ExcelWriter("JPMQuant_Backtest.xlsx") as writer:
            for k, v in export_data.items():
                v.to_excel(writer, sheet_name=k)
        st.success("Excel file 'JPMQuant_Backtest.xlsx' saved!")
