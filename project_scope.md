# QuantSense: Professional Probabilistic Stock Dashboard

## 1. Project Vision
**QuantSense** is designed to bridge the gap between retail trading and institutional-grade quantitative analysis. It transforms raw market data into actionable high-probability trading signals using a multi-factor weighted scoring engine.

---

## 2. Core Functionalities

### 🔍 Real-Time Data & Search
- **NSE Market Connectivity**: Seamless lookup for any ticker on the National Stock Exchange (NSE).
- **Intelligent Ticker Handling**: Automatically handles Indian stock suffixes (e.g., `.NS`) for a smoother search experience.
- **Historical Context**: Fetches up to 1 year of daily resolution data to provide a robust statistical sample for indicators.

### 📊 Multi-Panel Synchronized Dashboard
- **Price Action Panel**: High-performance candlesticks overlaid with:
    - **SMA 20**: Short-term trend baseline.
    - **VWAP**: Institutional "fair value" anchor.
    - **Ichimoku Cloud**: Advanced support/resistance and trend forecasting.
- **Volume Profile Panel**: Visualizes buy/sell pressure with color-coded volume histograms.
- **Momentum & Timing Panel**: A unified oscillator view featuring:
    - **RSI (14)**: Relative strength and overbought/oversold conditions.
    - **Stochastic (14, 3)**: Speed and momentum of price movements.
    - **ADX (14)**: Trend strength index.
    - **MACD Histograms**: Dual-axis view for precise entry/exit timing.

### 🧠 Probabilistic Scoring Engine
The app calculates a **Net Confidence Score (-100 to +100)** based on 4 primary quantitative categories:
1.  **Trend (35 pts)**: Validates if the path of least resistance is up or down using SMA/ADX/Ichimoku.
2.  **Momentum (25 pts)**: Identifies if price moves are accelerating or exhausting via RSI/Stochastic.
3.  **Timing (20 pts)**: Pinpoints specific entry "windows" using MACD and VWAP.
4.  **Confirmation (20 pts)**: Cross-references volume and volatility (Bollinger Bands) to filter out "fake-outs."

### 📝 Algorithmic Transparency
- Avoids "Black Box" signals by providing a **Logic Breakdown**.
- Every "Buy" or "Sell" signal includes the specific mathematical reasons from each category (e.g., *"+10: Price is securely above the Ichimoku Cloud"*).

---

## 3. Technical Stack

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Frontend** | React (Vite) | Fast, modular, and reactive UI updates. |
| **Styling** | Material UI (MUI) | Professional, consistent design system with pre-built components. |
| **Charting** | TradingView Lightweight Charts | Industry standard for fast, interactive financial charts. |
| **Backend** | Flask (Python) | Lightweight API for handling heavy data processing. |
| **Data Source** | `yfinance` | Reliable access to global and Indian market data. |
| **Indicator Logic** | `ta` (Technical Analysis Library) | Vectorized calculations for institutional-grade reliability. |

---

## 4. Proposed Roadmap (Future Scope)

- [ ] **Phase 2: Backtesting**: Allow users to see how often the scoring engine's signals have been correct in the past 6 months.
- [ ] **Phase 3: Custom Weighting**: Enable power users to adjust the importance of RSI vs. MACD in the final score.
- [ ] **Phase 4: Multi-Timeframe Analysis**: Fetch and compare daily vs. weekly signals for stronger confirmation.
- [ ] **Phase 5: Sentiment AI**: Integrate a Transformer model to analyze financial news headlines and adjust the confidence score based on news sentiment.

---

> [!NOTE]
> This project currently focuses on the National Stock Exchange (NSE) but the architecture is scalable to international markets (NYSE, NASDAQ) with minimal configuration changes.
