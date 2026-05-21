from flask import Flask, jsonify
from flask_cors import CORS
import yfinance as yf
import pandas as pd
import ta
import numpy as np

app = Flask(__name__)
CORS(app)

NIFTY_50_STOCKS = [
    {"ticker": "^NSEI", "name": "NIFTY 50 (Index)"},
    {"ticker": "RELIANCE.NS", "name": "Reliance Industries"},
    {"ticker": "TCS.NS", "name": "Tata Consultancy Services"},
    {"ticker": "HDFCBANK.NS", "name": "HDFC Bank"},
    {"ticker": "INFY.NS", "name": "Infosys"},
    {"ticker": "ICICIBANK.NS", "name": "ICICI Bank"}
]

@app.route('/api/stocks')
def get_stocks():
    return jsonify(NIFTY_50_STOCKS)

@app.route('/api/stock/<ticker>')
def get_stock_data(ticker):
    try:
        # Fetch 1 year of daily data to make the daily candles clearly visible
        stock = yf.Ticker(ticker)
        df = stock.history(period="1y")
        
        if df.empty:
            return jsonify({"error": "No data found for ticker"}), 404
            
        # Reset index to have Date as a column
        df = df.reset_index()
        # Ensure we just have a string date for JSON
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
        elif 'Datetime' in df.columns:
            df['Date'] = pd.to_datetime(df['Datetime']).dt.strftime('%Y-%m-%d')
            
        # Drop NaN Close rows
        df = df.dropna(subset=['Close'])
            
        # Calculate indicators
        # RSI 14
        df['rsi'] = ta.momentum.RSIIndicator(close=df['Close'], window=14).rsi()
        
        # SMA 20
        df['sma20'] = ta.trend.SMAIndicator(close=df['Close'], window=20).sma_indicator()
        
        # MACD 12, 26, 9
        macd = ta.trend.MACD(close=df['Close'], window_slow=26, window_fast=12, window_sign=9)
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_hist'] = macd.macd_diff()
        
        # Bollinger Bands 20, 2
        bb = ta.volatility.BollingerBands(close=df['Close'], window=20, window_dev=2)
        df['bb_upper'] = bb.bollinger_hband()
        df['bb_lower'] = bb.bollinger_lband()
        df['bb_mid'] = bb.bollinger_mavg()

        # ADX 14
        adx_ind = ta.trend.ADXIndicator(high=df['High'], low=df['Low'], close=df['Close'], window=14)
        df['adx'] = adx_ind.adx()
        df['adx_pos'] = adx_ind.adx_pos()
        df['adx_neg'] = adx_ind.adx_neg()

        # Stochastic Oscillator (14, 3)
        stoch_ind = ta.momentum.StochasticOscillator(high=df['High'], low=df['Low'], close=df['Close'], window=14, smooth_window=3)
        df['stoch'] = stoch_ind.stoch()
        df['stoch_signal'] = stoch_ind.stoch_signal()

        # VWAP
        vwap_ind = ta.volume.VolumeWeightedAveragePrice(high=df['High'], low=df['Low'], close=df['Close'], volume=df['Volume'])
        df['vwap'] = vwap_ind.volume_weighted_average_price()

        # Ichimoku Cloud
        ichimoku = ta.trend.IchimokuIndicator(high=df['High'], low=df['Low'])
        df['ichimoku_a'] = ichimoku.ichimoku_a()
        df['ichimoku_b'] = ichimoku.ichimoku_b()

        # Volume SMA 20
        df['volume_sma20'] = df['Volume'].rolling(window=20).mean()

        # Fibonacci Retracement (Rolling 50 Days)
        df['rolling_high'] = df['High'].rolling(50).max()
        df['rolling_low'] = df['Low'].rolling(50).min()
        df['fib_382'] = df['rolling_high'] - 0.382 * (df['rolling_high'] - df['rolling_low'])
        df['fib_618'] = df['rolling_high'] - 0.618 * (df['rolling_high'] - df['rolling_low'])
        
        # Replace NaN with None for JSON encoding
        df = df.replace({np.nan: None, float('nan'): None})
        
        # Logic for signals (based on latest valid data point)
        if len(df) < 2:
            return jsonify({"error": "Not enough data points"}), 400
            
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        total_score = 0
        categories = {
            "Trend": [],
            "Momentum": [],
            "Timing": [],
            "Confirmation": []
        }
        
        def safe_get(val, default_val=0):
            return val if val is not None else default_val

        # --- 1. TREND (35 points) ---
        close_p = safe_get(latest['Close'])
        sma20_p = safe_get(latest['sma20'])
        
        if close_p > sma20_p:
            total_score += 15
            categories['Trend'].append("+15: Price is above trending SMA 20.")
        else:
            total_score -= 15
            categories['Trend'].append("-15: Price is below SMA 20.")
            
        adx_v = safe_get(latest['adx'])
        adx_p = safe_get(latest['adx_pos'])
        adx_n = safe_get(latest['adx_neg'])
        if adx_v > 25:
            if adx_p > adx_n:
                total_score += 10
                categories['Trend'].append("+10: ADX > 25 showing strong uptrend (+DI > -DI).")
            else:
                total_score -= 10
                categories['Trend'].append("-10: ADX > 25 showing strong downtrend (-DI > +DI).")
        else:
            categories['Trend'].append("  0: ADX < 25 indicates weak or sideways trend.")
            
        ichi_a = safe_get(latest['ichimoku_a'])
        ichi_b = safe_get(latest['ichimoku_b'])
        if ichi_a and ichi_b:
            cloud_top = max(ichi_a, ichi_b)
            cloud_bottom = min(ichi_a, ichi_b)
            if close_p > cloud_top:
                total_score += 10
                categories['Trend'].append("+10: Price is securely above the Ichimoku Cloud.")
            elif close_p < cloud_bottom:
                total_score -= 10
                categories['Trend'].append("-10: Price is buried below the Ichimoku Cloud.")
            else:
                categories['Trend'].append("  0: Price is stuck inside the Ichimoku Cloud (Neutral).")
        else:
            categories['Trend'].append("  0: Ichimoku data unavailable.")

        # --- 2. MOMENTUM (25 points) ---
        rsi_v = safe_get(latest['rsi'], 50)
        rsi_prev = safe_get(prev['rsi'], 50)
        if rsi_v < 30 or (40 <= rsi_v <= 60 and rsi_v > rsi_prev):
            total_score += 15
            categories['Momentum'].append("+15: RSI is oversold or bouncing dynamically.")
        elif rsi_v > 70 or (40 <= rsi_v <= 60 and rsi_v < rsi_prev):
            total_score -= 15
            categories['Momentum'].append("-15: RSI is overbought or facing rejection.")
        else:
            categories['Momentum'].append("  0: RSI is neutral and floating.")
            
        stoch_v = safe_get(latest['stoch'], 50)
        stoch_sig = safe_get(latest['stoch_signal'], 50)
        if stoch_v < 20 and stoch_v > stoch_sig:
            total_score += 10
            categories['Momentum'].append("+10: Stochastic Oscillator implies bullish flip.")
        elif stoch_v > 80 and stoch_v < stoch_sig:
            total_score -= 10
            categories['Momentum'].append("-10: Stochastic Oscillator implies bearish fade.")
        else:
            categories['Momentum'].append("  0: Stochastic Oscillator is neutral.")

        # --- 3. TIMING (20 points) ---
        macd_v = safe_get(latest['macd'])
        macd_sig = safe_get(latest['macd_signal'])
        if macd_v > macd_sig:
            total_score += 10
            categories['Timing'].append("+10: MACD generated bullish timing.")
        else:
            total_score -= 10
            categories['Timing'].append("-10: MACD generated bearish timing.")
            
        vwap_v = safe_get(latest['vwap'])
        if close_p > vwap_v:
            total_score += 10
            categories['Timing'].append("+10: Price maintains structural bid (Above VWAP).")
        else:
            total_score -= 10
            categories['Timing'].append("-10: Price is weighed down heavily (Below VWAP).")

        # --- 4. CONFIRMATION (20 points) ---
        bb_u = safe_get(latest['bb_upper'])
        bb_l = safe_get(latest['bb_lower'])
        if bb_u and bb_l:
            bb_width = bb_u - bb_l
            if close_p <= bb_l + 0.2 * bb_width:
                total_score += 10
                categories['Confirmation'].append("+10: Price is bouncing optimally off Lower Bollinger Band.")
            elif close_p >= bb_u - 0.2 * bb_width:
                total_score -= 10
                categories['Confirmation'].append("-10: Price indicates short exhaustion at Upper Bollinger Band.")
            else:
                categories['Confirmation'].append("  0: Volatility bands lack clear bounds currently.")
        else:
            categories['Confirmation'].append("  0: Volatility data limited.")
            
        vol_p = safe_get(latest['Volume'])
        vol_sma20 = safe_get(latest['volume_sma20'])
        if vol_p > vol_sma20:
            if total_score > 0:
                total_score += 10
                categories['Confirmation'].append("+10: Heavy buying volume validates the breakout direction.")
            elif total_score < 0:
                total_score -= 10
                categories['Confirmation'].append("-10: Heavy selling volume validates the dump momentum.")
            else:
                categories['Confirmation'].append("  0: High volume rotation with no structural bias.")
        else:
            categories['Confirmation'].append("  0: Routine trading volume provides no particular confidence.")

        signal = "Hold"
        if total_score >= 60:
            signal = "Buy"
        elif total_score <= -60:
            signal = "Sell"

        # Prepare historical data for lightweight-charts
        chart_data = []
        for _, row in df.iterrows():
            chart_data.append({
                "time": row["Date"],
                "open": row["Open"],
                "high": row["High"],
                "low": row["Low"],
                "close": row["Close"],
                "volume": row["Volume"],
                "rsi": row["rsi"],
                "sma20": row["sma20"],
                "macd": row["macd"],
                "macd_signal": row["macd_signal"],
                "macd_hist": row["macd_hist"],
                "bb_upper": row["bb_upper"],
                "bb_lower": row["bb_lower"],
                "bb_mid": row["bb_mid"],
                "stoch": row["stoch"],
                "stoch_signal": row["stoch_signal"],
                "adx": row["adx"],
                "vwap": row["vwap"]
            })
            
        response = {
            "ticker": ticker,
            "signal": signal,
            "score": total_score,
            "categories": categories,
            "data": chart_data,
            "latest": {
                "close": latest["Close"],
                "rsi": latest["rsi"],
                "sma20": latest["sma20"]
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
