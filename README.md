## RVNL Stock Forecasting and Trading Strategy using LSTM, Transformer, and XGBoost

This project proposes a hybrid AI-driven pipeline for stock market prediction and trading signal generation, applied to **RVNL (Rail Vikas Nigam Limited)**—a mid-cap equity traded on the NSE. The pipeline integrates deep learning (LSTM, Transformer), tree-based ensemble learning (XGBoost), explainable AI (SHAP, Attention), and quantitative trading logic for generating actionable buy/sell signals.

🔒 The repository will be made public post-acceptance of our research paper submitted to an ACM international conference.

---

## 🔍 Core Objectives

1. **Forecasting Returns:** Predict log returns over a fixed horizon (Δt).
2. **Trading Signal Generation:** Convert predictions into decisions using mathematically defined thresholds.
3. **Performance Evaluation:** Benchmark strategy vs. market baselines using risk-adjusted metrics.
4. **Risk Analysis:** Cinvert Predicted and actual model to calculate risk analysis using graph

---

## 🧠 Mathematical Formulation

### 1. **Returns Prediction**

We model log-returns \( r_t \) as:

\[
r_t = \log\left(\frac{P_t}{P_{t-1}}\right)
\]

Where:
- \( P_t \) is the closing price at time \( t \)
- \( r_t \) is the predicted return fed into the trading signal logic

---

### 2. **LSTM Model**

The LSTM cell evolves as:

\[
\begin{aligned}
f_t &= \sigma(W_f \cdot [h_{t-1}, x_t] + b_f) \\
i_t &= \sigma(W_i \cdot [h_{t-1}, x_t] + b_i) \\
\tilde{C}_t &= \tanh(W_C \cdot [h_{t-1}, x_t] + b_C) \\
C_t &= f_t \cdot C_{t-1} + i_t \cdot \tilde{C}_t \\
o_t &= \sigma(W_o \cdot [h_{t-1}, x_t] + b_o) \\
h_t &= o_t \cdot \tanh(C_t)
\end{aligned}
\]

---

### 3. **Transformer Self-Attention**

\[
\text{Attention}(Q, K, V) = \text{softmax} \left( \frac{QK^T}{\sqrt{d_k}} \right) V
\]

Where:
- \( Q, K, V \) are projections of the input sequence
- \( d_k \) is the dimension of the key vectors

---

### 4. **Trading Signal Generation**

Let \( \hat{r}_t \) be the predicted return at time \( t \):

\[
\text{Signal}_t =
\begin{cases}
\text{Buy}, & \hat{r}_t > \theta^+ \\
\text{Sell}, & \hat{r}_t < \theta^- \\
\text{Hold}, & \text{otherwise}
\end{cases}
\]

Where \( \theta^+ \) and \( \theta^- \) are the upper and lower return thresholds respectively (e.g., dynamic quantiles).

---

### 5. **Performance Metrics**

- **Cumulative Return**:

\[
R_T = \prod_{t=1}^{T} (1 + r_t^{\text{strategy}}) - 1
\]

- **Sharpe Ratio**:

\[
\text{Sharpe} = \frac{E[R_p - R_f]}{\sigma_p}
\]

- **Sortino Ratio**:

\[
\text{Sortino} = \frac{E[R_p - R_f]}{\sigma_d}
\]

Where:
- \( R_p \) is portfolio return
- \( R_f \) is the risk-free rate
- \( \sigma_d \) is downside deviation

- **Maximum Drawdown**:

\[
\text{MDD} = \max_{t \in [1,T]} \left( \frac{\max_{s \in [1,t]} P_s - P_t}{\max_{s \in [1,t]} P_s} \right)
\]

---

## 📈 Feature Engineering

- **Technical Indicators**:
  - RSI, MACD, EMA/SMA crossover, Bollinger Bands, ATR
- **Lag Features**:
  - \( r_{t-1}, r_{t-2}, \ldots \)
- **Rolling Statistics**:
  - Rolling mean/variance, momentum
- **Autocorrelation Measures**
- **Target Variable**:
  - Binary classification (Up/Down), Regression (future returns)

---

## 🔍 Explainable AI

- **SHAP Values**:
  \[
  f(x) = \phi_0 + \sum_{i=1}^{M} \phi_i
  \]
  where \( \phi_i \) quantifies each feature's contribution.
- **Transformer Attention Heatmaps**:
  Visualizes which timesteps/models attend to most for forecasting.

---

## 💹 Risk Analysis

- **Volatility Modeling**
- **Residual Analysis** (Autocorrelation and Heteroskedasticity)
- **Skewness & Kurtosis**
- **Probabilistic Confidence Bands**

---

## 🧪 Backtesting Logic

- Walk-forward validation
- Daily returns aggregation
- Equity curve simulation
- Market impact ignored for baseline tests

---

## 📊 Benchmarks

- **Buy & Hold**
- **SMA/EMA crossover**
- **RSI reversal strategy**
- **Random Forest classifier (baseline)**

---

## 🔧 Future Enhancements

- Integration with broker APIs for live paper-trading
- Reinforcement Learning-based signal optimization
- Multivariate prediction (News sentiment + stock price)
- Volatility-adjusted dynamic thresholds

---

## 📌 Citation

📄 If you use this work or reference our pipeline, please cite the research paper upon release.

---

## 🛑 Disclaimer

This project is purely academic and **does not constitute financial advice**. All trading strategies must be backtested and validated before live deployment.
