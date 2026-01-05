### Advanced Stock Prediction Dashboard

A fully interactive quantitative trading research platform built with Python, Streamlit, and Plotly. It fetches market data, computes technical indicators, generates trading signals, and runs a multi-asset portfolio backtest with detailed analytics and visualizations.

----------------------------------------------------------------------------------------------------

🚀 FEATURES

• Multi-Asset Backtesting Engine
  - Supports unlimited tickers
  - Dynamic cash allocation
  - Slippage & commissions
  - Trade-by-trade logs
  - Portfolio equity curve
  - Sharpe, CAGR, Max Drawdown, Calmar, Sortino, Omega

• Strategy Framework
  - EMA + RSI + Volatility Filter
  - Bollinger Mean Reversion
  - MACD Trend Following
  - Plug-and-play for custom strategies

• Technical Indicators
  - EMA (fast/slow)
  - RSI
  - Volatility (rolling)
  - Bollinger Bands
  - MACD (line/signal/hist)
  - ATR
  - Log returns & derived features
    
• Visualization Dashboard
  - Interactive equity curve (Plotly)
  - Per-ticker risk vs return scatter
  - Sortino-colored performance map
  - Per-ticker trade chart (entries/exits)
  - Indicator overlays (EMA, MACD, BB, ATR)
  - Filterable and dynamic through Streamlit

• Export Tools
  - Excel export with all trade logs
  - Portfolio equity curve included

----------------------------------------------------------------------------------------------------

🏗️ PROJECT STRUCTURE

project/
├── app.py                # Streamlit dashboard
├── data_loader.py        # fetch_price_data()
├── features.py           # technical indicators + feature prep
├── strategies.py         # signal generation logic
├── backtester.py         # portfolio backtesting engine
└── README.md

----------------------------------------------------------------------------------------------------

▶️ RUN THE DASHBOARD
<img width="2534" height="1408" alt="Screenshot 2025-10-25 231059" src="https://github.com/user-attachments/assets/8ba1934d-9ff1-4987-a919-14c914e1a983" />
