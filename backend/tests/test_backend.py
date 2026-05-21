"""
=============================================================================
 QuantSense — White Box Branch Coverage Tests
 Target: backend/app.py → get_stock_data() scoring engine
 Strategy: Mock yfinance + all 8 ta-lib indicator classes to inject precise
           values into each branch of the scoring logic (Lines 96-229)
 Coverage tool: pytest-cov (branch mode)
 Run:  cd backend && pytest tests/test_backend.py -v --cov=app --cov-branch
=============================================================================
"""

import pytest
import json
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np

# ── Import the Flask app under test ─────────────────────────────────────────
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app import app


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════

NUM_ROWS = 60  # Enough for rolling(50) calculations to produce non-NaN


def _make_ohlcv(n=NUM_ROWS, close=100.0, volume=1_000_000.0):
    """Generate a basic OHLCV DataFrame mimicking yfinance output.

    Uses Python floats throughout to avoid numpy int64 JSON serialization
    errors in Flask's jsonify.
    """
    dates = pd.date_range('2025-01-01', periods=n, freq='B')
    df = pd.DataFrame({
        'Open':   [float(close - 2)] * n,
        'High':   [float(close + 5)] * n,
        'Low':    [float(close - 5)] * n,
        'Close':  [float(close)] * n,
        'Volume': [float(volume)] * n,
    }, index=dates)
    df.index.name = 'Date'
    return df


def _make_series(n, *values):
    """Create a float pd.Series of length n.

    If one value:   constant series.
    If two values:  series[:-1] = first, series[-1] = second.
    If three values: series[:-2] = first, series[-2] = second, series[-1] = third.
    """
    if len(values) == 1:
        v = None if values[0] is None else float(values[0])
        return pd.Series([v] * n, dtype='object' if v is None else 'float64')
    elif len(values) == 2:
        base = None if values[0] is None else float(values[0])
        last = None if values[1] is None else float(values[1])
        data = [base] * n
        data[-1] = last
        return pd.Series(data, dtype='object' if base is None else 'float64')
    elif len(values) == 3:
        base = None if values[0] is None else float(values[0])
        prev = None if values[1] is None else float(values[1])
        last = None if values[2] is None else float(values[2])
        data = [base] * n
        if n >= 2:
            data[-2] = prev
        data[-1] = last
        return pd.Series(data, dtype='object' if base is None else 'float64')


def _configure_ta_mocks(
    mocks, n=NUM_ROWS,
    rsi=50.0, rsi_prev=None,
    sma20=100.0,
    macd_val=1.0, macd_sig=0.5, macd_hist=0.5,
    bb_upper=110.0, bb_lower=90.0, bb_mid=100.0,
    adx=30.0, adx_pos=20.0, adx_neg=15.0,
    stoch=50.0, stoch_signal=50.0,
    vwap=100.0,
    ichi_a=100.0, ichi_b=98.0,
):
    """Wire up all 8 ta-lib mock objects with float values.

    `mocks` is a dict of mock objects keyed by short name.
    """
    rsi_prev = rsi_prev if rsi_prev is not None else rsi

    # RSI — needs prev and latest
    m = mocks['rsi']
    inst = MagicMock()
    inst.rsi.return_value = _make_series(n, 50.0, float(rsi_prev), float(rsi))
    m.return_value = inst

    # SMA
    m = mocks['sma']
    inst = MagicMock()
    inst.sma_indicator.return_value = _make_series(n, float(sma20))
    m.return_value = inst

    # MACD
    m = mocks['macd']
    inst = MagicMock()
    inst.macd.return_value = _make_series(n, float(macd_val))
    inst.macd_signal.return_value = _make_series(n, float(macd_sig))
    inst.macd_diff.return_value = _make_series(n, float(macd_hist))
    m.return_value = inst

    # Bollinger Bands
    m = mocks['bb']
    inst = MagicMock()
    if bb_upper is None:
        inst.bollinger_hband.return_value = _make_series(n, None)
        inst.bollinger_lband.return_value = _make_series(n, None)
        inst.bollinger_mavg.return_value = _make_series(n, None)
    else:
        inst.bollinger_hband.return_value = _make_series(n, float(bb_upper))
        inst.bollinger_lband.return_value = _make_series(n, float(bb_lower))
        inst.bollinger_mavg.return_value = _make_series(n, float(bb_mid))
    m.return_value = inst

    # ADX
    m = mocks['adx']
    inst = MagicMock()
    inst.adx.return_value = _make_series(n, float(adx))
    inst.adx_pos.return_value = _make_series(n, float(adx_pos))
    inst.adx_neg.return_value = _make_series(n, float(adx_neg))
    m.return_value = inst

    # Stochastic
    m = mocks['stoch']
    inst = MagicMock()
    inst.stoch.return_value = _make_series(n, float(stoch))
    inst.stoch_signal.return_value = _make_series(n, float(stoch_signal))
    m.return_value = inst

    # VWAP
    m = mocks['vwap']
    inst = MagicMock()
    inst.volume_weighted_average_price.return_value = _make_series(n, float(vwap))
    m.return_value = inst

    # Ichimoku
    m = mocks['ichi']
    inst = MagicMock()
    if ichi_a is None:
        inst.ichimoku_a.return_value = _make_series(n, None)
        inst.ichimoku_b.return_value = _make_series(n, None)
    else:
        inst.ichimoku_a.return_value = _make_series(n, float(ichi_a))
        inst.ichimoku_b.return_value = _make_series(n, float(ichi_b))
    m.return_value = inst


# ── Stacked-patch order (bottom-up → left-to-right in function params) ──────
PATCH_STACK = [
    'app.ta.volume.VolumeWeightedAveragePrice',   # → mock_vwap
    'app.ta.trend.IchimokuIndicator',              # → mock_ichi
    'app.ta.momentum.StochasticOscillator',        # → mock_stoch
    'app.ta.trend.ADXIndicator',                   # → mock_adx
    'app.ta.volatility.BollingerBands',            # → mock_bb
    'app.ta.trend.MACD',                           # → mock_macd
    'app.ta.trend.SMAIndicator',                   # → mock_sma
    'app.ta.momentum.RSIIndicator',                # → mock_rsi
    'app.yf.Ticker',                               # → mock_yf
]


def _unpack_mocks(mock_yf, mock_rsi, mock_sma, mock_macd,
                  mock_bb, mock_adx, mock_stoch, mock_ichi, mock_vwap):
    """Unpack the 9 positional mock args into a handy dict."""
    return {
        'yf': mock_yf, 'rsi': mock_rsi, 'sma': mock_sma,
        'macd': mock_macd, 'bb': mock_bb, 'adx': mock_adx,
        'stoch': mock_stoch, 'ichi': mock_ichi, 'vwap': mock_vwap,
    }


# ── Flask test client ──────────────────────────────────────────────────────
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


# ══════════════════════════════════════════════════════════════════════════════
#  WB-01  MAXIMUM BULLISH → Score +100, Signal "Buy"
# ══════════════════════════════════════════════════════════════════════════════
#  Branches hit (True path):
#    B1T  (close > sma20)            +15
#    B2T  (adx > 25)
#    B3T  (+DI > -DI)                +10
#    B4T  (ichimoku data available)
#    B5T  (price above cloud)        +10
#    B7T  (RSI < 30 oversold)        +15
#    B9T  (stoch < 20, stoch > sig)  +10
#    B11T (MACD > signal)            +10
#    B12T (close > VWAP)             +10
#    B13T (BB data available)
#    B14T (price near lower BB)      +10
#    B16T (vol > vol_sma20)
#    B17T (total_score > 0)          +10
#                                   ─────
#                             Total: +100
# ══════════════════════════════════════════════════════════════════════════════

@patch(PATCH_STACK[0])
@patch(PATCH_STACK[1])
@patch(PATCH_STACK[2])
@patch(PATCH_STACK[3])
@patch(PATCH_STACK[4])
@patch(PATCH_STACK[5])
@patch(PATCH_STACK[6])
@patch(PATCH_STACK[7])
@patch(PATCH_STACK[8])
def test_wb01_maximum_bullish(mock_yf, mock_rsi, mock_sma, mock_macd,
                              mock_bb, mock_adx, mock_stoch, mock_ichi,
                              mock_vwap, client):
    """All bullish branches → Score = +100, Signal = Buy."""
    n = NUM_ROWS
    mocks = _unpack_mocks(mock_yf, mock_rsi, mock_sma, mock_macd,
                          mock_bb, mock_adx, mock_stoch, mock_ichi, mock_vwap)

    # OHLCV: close=110, last-row volume spike for volume confirmation
    df = _make_ohlcv(n, close=110.0, volume=1_000_000.0)
    df.iloc[-1, df.columns.get_loc('Volume')] = 2_500_000.0
    mocks['yf'].return_value.history.return_value = df

    _configure_ta_mocks(
        mocks, n,
        rsi=25.0,                        # B7T:  RSI < 30 (oversold)
        sma20=100.0,                     # B1T:  110 > 100
        macd_val=2.0, macd_sig=1.0,      # B11T: MACD > signal
        bb_upper=130.0, bb_lower=108.0, bb_mid=119.0,  # B14T: 110<=108+0.2*22=112.4
        adx=30.0, adx_pos=25.0, adx_neg=15.0,          # B2T, B3T
        stoch=15.0, stoch_signal=10.0,                  # B9T: <20 AND >signal
        vwap=100.0,                      # B12T: 110 > 100
        ichi_a=105.0, ichi_b=103.0,      # B4T, B5T: 110 > cloud_top(105)
    )

    response = client.get('/api/stock/TEST.NS')
    data = json.loads(response.data)

    assert response.status_code == 200
    assert data['score'] == 100
    assert data['signal'] == 'Buy'
    assert len(data['categories']['Trend']) == 3
    assert len(data['categories']['Momentum']) == 2
    assert len(data['categories']['Timing']) == 2
    assert len(data['categories']['Confirmation']) == 2


# ══════════════════════════════════════════════════════════════════════════════
#  WB-02  MAXIMUM BEARISH → Score -100, Signal "Sell"
# ══════════════════════════════════════════════════════════════════════════════
#  Branches hit (False / bearish path):
#    B1F  (close ≤ sma20)             -15
#    B2T  (adx > 25)
#    B3F  (-DI > +DI)                 -10
#    B4T  (ichimoku available)
#    B6T  (price below cloud)         -10
#    B8T  (RSI > 70 overbought)       -15
#    B10T (stoch > 80, stoch < sig)   -10
#    B11F (MACD ≤ signal)             -10
#    B12F (close ≤ VWAP)              -10
#    B13T (BB available)
#    B15T (price near upper BB)       -10
#    B16T (vol > sma)
#    B18T (total_score < 0)           -10
#                                    ─────
#                              Total: -100
# ══════════════════════════════════════════════════════════════════════════════

@patch(PATCH_STACK[0])
@patch(PATCH_STACK[1])
@patch(PATCH_STACK[2])
@patch(PATCH_STACK[3])
@patch(PATCH_STACK[4])
@patch(PATCH_STACK[5])
@patch(PATCH_STACK[6])
@patch(PATCH_STACK[7])
@patch(PATCH_STACK[8])
def test_wb02_maximum_bearish(mock_yf, mock_rsi, mock_sma, mock_macd,
                              mock_bb, mock_adx, mock_stoch, mock_ichi,
                              mock_vwap, client):
    """All bearish branches → Score = -100, Signal = Sell."""
    n = NUM_ROWS
    mocks = _unpack_mocks(mock_yf, mock_rsi, mock_sma, mock_macd,
                          mock_bb, mock_adx, mock_stoch, mock_ichi, mock_vwap)

    df = _make_ohlcv(n, close=90.0, volume=1_000_000.0)
    df.iloc[-1, df.columns.get_loc('Volume')] = 2_500_000.0
    mocks['yf'].return_value.history.return_value = df

    _configure_ta_mocks(
        mocks, n,
        rsi=75.0,                        # B8T:  RSI > 70
        sma20=100.0,                     # B1F:  90 ≤ 100
        macd_val=-1.0, macd_sig=1.0,     # B11F: -1 ≤ 1
        bb_upper=92.0, bb_lower=70.0, bb_mid=81.0,  # B15T: 90>=92-0.2*22=87.6
        adx=30.0, adx_pos=15.0, adx_neg=25.0,       # B2T, B3F: -DI > +DI
        stoch=85.0, stoch_signal=90.0,               # B10T: >80 AND <signal
        vwap=100.0,                      # B12F: 90 ≤ 100
        ichi_a=95.0, ichi_b=93.0,        # B4T, B6T: 90 < cloud_bottom(93)
    )

    response = client.get('/api/stock/TEST.NS')
    data = json.loads(response.data)

    assert response.status_code == 200
    assert data['score'] == -100
    assert data['signal'] == 'Sell'


# ══════════════════════════════════════════════════════════════════════════════
#  WB-03  NEUTRAL — All zero/weak branches → Hold
# ══════════════════════════════════════════════════════════════════════════════
#  Branches hit:
#    B1F  (close ≤ sma20)            -15
#    B2F  (adx ≤ 25 → weak)           0
#    B4T  (ichi available)
#    B5F, B6F (inside cloud)           0
#    B7F, B8F (RSI neutral 35)         0
#    B9F, B10F (stoch neutral 50)      0
#    B11F (MACD ≤ signal)            -10
#    B12F (close ≤ VWAP)             -10
#    B13T (BB available)
#    B14F, B15F (price mid-BB)         0
#    B16F (vol ≤ sma)                  0
#                                   ─────
#                             Total: -35  → Hold
# ══════════════════════════════════════════════════════════════════════════════

@patch(PATCH_STACK[0])
@patch(PATCH_STACK[1])
@patch(PATCH_STACK[2])
@patch(PATCH_STACK[3])
@patch(PATCH_STACK[4])
@patch(PATCH_STACK[5])
@patch(PATCH_STACK[6])
@patch(PATCH_STACK[7])
@patch(PATCH_STACK[8])
def test_wb03_neutral_hold(mock_yf, mock_rsi, mock_sma, mock_macd,
                           mock_bb, mock_adx, mock_stoch, mock_ichi,
                           mock_vwap, client):
    """All neutral / zero-score branches → Score = -35, Signal = Hold."""
    n = NUM_ROWS
    mocks = _unpack_mocks(mock_yf, mock_rsi, mock_sma, mock_macd,
                          mock_bb, mock_adx, mock_stoch, mock_ichi, mock_vwap)

    df = _make_ohlcv(n, close=100.0, volume=1_000_000.0)
    mocks['yf'].return_value.history.return_value = df

    _configure_ta_mocks(
        mocks, n,
        rsi=35.0, rsi_prev=35.0,                    # B7F, B8F: not in any active range
        sma20=100.0,                                 # B1F: 100 ≤ 100 (not strict >)
        macd_val=0.0, macd_sig=0.0,                  # B11F: 0 ≤ 0
        bb_upper=110.0, bb_lower=90.0, bb_mid=100.0, # mid-band: not ≤94, not ≥106
        adx=20.0, adx_pos=10.0, adx_neg=10.0,       # B2F: 20 ≤ 25
        stoch=50.0, stoch_signal=50.0,               # B9F, B10F: neutral
        vwap=100.0,                                  # B12F: 100 ≤ 100
        ichi_a=101.0, ichi_b=99.0,                   # inside cloud: 99<100<101
    )

    response = client.get('/api/stock/TEST.NS')
    data = json.loads(response.data)

    assert response.status_code == 200
    assert data['score'] == -35
    assert data['signal'] == 'Hold'


# ══════════════════════════════════════════════════════════════════════════════
#  WB-04  ICHIMOKU UNAVAILABLE → Branch B4F
# ══════════════════════════════════════════════════════════════════════════════

@patch(PATCH_STACK[0])
@patch(PATCH_STACK[1])
@patch(PATCH_STACK[2])
@patch(PATCH_STACK[3])
@patch(PATCH_STACK[4])
@patch(PATCH_STACK[5])
@patch(PATCH_STACK[6])
@patch(PATCH_STACK[7])
@patch(PATCH_STACK[8])
def test_wb04_ichimoku_unavailable(mock_yf, mock_rsi, mock_sma, mock_macd,
                                   mock_bb, mock_adx, mock_stoch, mock_ichi,
                                   mock_vwap, client):
    """Ichimoku returns None → safe_get yields 0 → B4F (falsy)."""
    n = NUM_ROWS
    mocks = _unpack_mocks(mock_yf, mock_rsi, mock_sma, mock_macd,
                          mock_bb, mock_adx, mock_stoch, mock_ichi, mock_vwap)

    df = _make_ohlcv(n, close=100.0, volume=1_000_000.0)
    mocks['yf'].return_value.history.return_value = df

    _configure_ta_mocks(
        mocks, n,
        rsi=35.0, rsi_prev=35.0,
        sma20=100.0,
        macd_val=0.0, macd_sig=0.0,
        bb_upper=110.0, bb_lower=90.0, bb_mid=100.0,
        adx=20.0, adx_pos=10.0, adx_neg=10.0,
        stoch=50.0, stoch_signal=50.0,
        vwap=100.0,
        ichi_a=None, ichi_b=None,  # ← B4F: both become 0 via safe_get
    )

    response = client.get('/api/stock/TEST.NS')
    data = json.loads(response.data)

    assert response.status_code == 200
    # Ichimoku unavailable message should be in Trend category
    trend_texts = ' '.join(data['categories']['Trend'])
    assert 'Ichimoku data unavailable' in trend_texts


# ══════════════════════════════════════════════════════════════════════════════
#  WB-05  BOLLINGER BANDS UNAVAILABLE → Branch B13F
# ══════════════════════════════════════════════════════════════════════════════

@patch(PATCH_STACK[0])
@patch(PATCH_STACK[1])
@patch(PATCH_STACK[2])
@patch(PATCH_STACK[3])
@patch(PATCH_STACK[4])
@patch(PATCH_STACK[5])
@patch(PATCH_STACK[6])
@patch(PATCH_STACK[7])
@patch(PATCH_STACK[8])
def test_wb05_bollinger_unavailable(mock_yf, mock_rsi, mock_sma, mock_macd,
                                    mock_bb, mock_adx, mock_stoch, mock_ichi,
                                    mock_vwap, client):
    """BB returns None → safe_get yields 0 → B13F (falsy)."""
    n = NUM_ROWS
    mocks = _unpack_mocks(mock_yf, mock_rsi, mock_sma, mock_macd,
                          mock_bb, mock_adx, mock_stoch, mock_ichi, mock_vwap)

    df = _make_ohlcv(n, close=100.0, volume=1_000_000.0)
    mocks['yf'].return_value.history.return_value = df

    _configure_ta_mocks(
        mocks, n,
        rsi=35.0, rsi_prev=35.0,
        sma20=100.0,
        macd_val=0.0, macd_sig=0.0,
        bb_upper=None, bb_lower=None, bb_mid=None,  # ← B13F
        adx=20.0, adx_pos=10.0, adx_neg=10.0,
        stoch=50.0, stoch_signal=50.0,
        vwap=100.0,
        ichi_a=101.0, ichi_b=99.0,
    )

    response = client.get('/api/stock/TEST.NS')
    data = json.loads(response.data)

    assert response.status_code == 200
    confirm_texts = ' '.join(data['categories']['Confirmation'])
    assert 'Volatility data limited' in confirm_texts


# ══════════════════════════════════════════════════════════════════════════════
#  WB-06  RSI NEUTRAL-ZONE RISING → Branch B7T (dynamic bounce)
# ══════════════════════════════════════════════════════════════════════════════
#  Condition: 40 ≤ RSI ≤ 60 AND RSI > RSI_prev
#  RSI = 45, prev = 40 → True → +15

@patch(PATCH_STACK[0])
@patch(PATCH_STACK[1])
@patch(PATCH_STACK[2])
@patch(PATCH_STACK[3])
@patch(PATCH_STACK[4])
@patch(PATCH_STACK[5])
@patch(PATCH_STACK[6])
@patch(PATCH_STACK[7])
@patch(PATCH_STACK[8])
def test_wb06_rsi_neutral_rising(mock_yf, mock_rsi, mock_sma, mock_macd,
                                 mock_bb, mock_adx, mock_stoch, mock_ichi,
                                 mock_vwap, client):
    """RSI rising in 40-60 zone → +15 momentum (B7T dynamic bounce)."""
    n = NUM_ROWS
    mocks = _unpack_mocks(mock_yf, mock_rsi, mock_sma, mock_macd,
                          mock_bb, mock_adx, mock_stoch, mock_ichi, mock_vwap)

    df = _make_ohlcv(n, close=100.0, volume=1_000_000.0)
    mocks['yf'].return_value.history.return_value = df

    _configure_ta_mocks(
        mocks, n,
        rsi=45.0, rsi_prev=40.0,        # ← B7T: 40 ≤ 45 ≤ 60 AND 45 > 40
        sma20=100.0,
        macd_val=0.0, macd_sig=0.0,
        bb_upper=110.0, bb_lower=90.0, bb_mid=100.0,
        adx=20.0, adx_pos=10.0, adx_neg=10.0,
        stoch=50.0, stoch_signal=50.0,
        vwap=100.0,
        ichi_a=101.0, ichi_b=99.0,
    )

    response = client.get('/api/stock/TEST.NS')
    data = json.loads(response.data)

    assert response.status_code == 200
    # Momentum gained +15 compared to WB-03's 0. Total: -35 + 15 = -20
    assert data['score'] == -20
    assert data['signal'] == 'Hold'
    momentum_texts = ' '.join(data['categories']['Momentum'])
    assert 'bouncing dynamically' in momentum_texts


# ══════════════════════════════════════════════════════════════════════════════
#  WB-07  RSI NEUTRAL-ZONE FALLING → Branch B8T (rejection)
# ══════════════════════════════════════════════════════════════════════════════
#  Condition: 40 ≤ RSI ≤ 60 AND RSI < RSI_prev
#  RSI = 55, prev = 58 → True → -15

@patch(PATCH_STACK[0])
@patch(PATCH_STACK[1])
@patch(PATCH_STACK[2])
@patch(PATCH_STACK[3])
@patch(PATCH_STACK[4])
@patch(PATCH_STACK[5])
@patch(PATCH_STACK[6])
@patch(PATCH_STACK[7])
@patch(PATCH_STACK[8])
def test_wb07_rsi_neutral_falling(mock_yf, mock_rsi, mock_sma, mock_macd,
                                  mock_bb, mock_adx, mock_stoch, mock_ichi,
                                  mock_vwap, client):
    """RSI falling in 40-60 zone → -15 momentum (B8T rejection)."""
    n = NUM_ROWS
    mocks = _unpack_mocks(mock_yf, mock_rsi, mock_sma, mock_macd,
                          mock_bb, mock_adx, mock_stoch, mock_ichi, mock_vwap)

    df = _make_ohlcv(n, close=100.0, volume=1_000_000.0)
    mocks['yf'].return_value.history.return_value = df

    _configure_ta_mocks(
        mocks, n,
        rsi=55.0, rsi_prev=58.0,        # ← B8T: 40 ≤ 55 ≤ 60 AND 55 < 58
        sma20=100.0,
        macd_val=0.0, macd_sig=0.0,
        bb_upper=110.0, bb_lower=90.0, bb_mid=100.0,
        adx=20.0, adx_pos=10.0, adx_neg=10.0,
        stoch=50.0, stoch_signal=50.0,
        vwap=100.0,
        ichi_a=101.0, ichi_b=99.0,
    )

    response = client.get('/api/stock/TEST.NS')
    data = json.loads(response.data)

    assert response.status_code == 200
    # WB-03 base is -35, but momentum changes from 0 to -15 → total -50
    assert data['score'] == -50
    assert data['signal'] == 'Hold'
    momentum_texts = ' '.join(data['categories']['Momentum'])
    assert 'facing rejection' in momentum_texts


# ══════════════════════════════════════════════════════════════════════════════
#  WB-08  HIGH VOLUME WITH NEUTRAL CUMULATIVE SCORE → B16T, B17F, B18F
# ══════════════════════════════════════════════════════════════════════════════
#  Engineered so total_score = 0 at the volume check point:
#    Trend:   +15 (above SMA) -10 (ADX downtrend) +10 (above cloud) = +15
#    Momentum: +15 (RSI oversold) +0 (stoch neutral) = +15
#    Timing:  -10 (MACD bearish) -10 (below VWAP) = -20
#    BB:      -10 (near upper band) = -10
#    Subtotal = +15 +15 -20 -10 = 0
#    Volume:  vol > sma → B16T, score=0 → B17F, B18F → +0
#    Total = 0 → Hold

@patch(PATCH_STACK[0])
@patch(PATCH_STACK[1])
@patch(PATCH_STACK[2])
@patch(PATCH_STACK[3])
@patch(PATCH_STACK[4])
@patch(PATCH_STACK[5])
@patch(PATCH_STACK[6])
@patch(PATCH_STACK[7])
@patch(PATCH_STACK[8])
def test_wb08_high_volume_neutral_score(mock_yf, mock_rsi, mock_sma, mock_macd,
                                        mock_bb, mock_adx, mock_stoch, mock_ichi,
                                        mock_vwap, client):
    """Volume spike when cumulative score is exactly 0 → no conf bonus (B17F, B18F)."""
    n = NUM_ROWS
    mocks = _unpack_mocks(mock_yf, mock_rsi, mock_sma, mock_macd,
                          mock_bb, mock_adx, mock_stoch, mock_ichi, mock_vwap)

    # Close=110 (above SMA, above cloud, but will be below VWAP=120)
    df = _make_ohlcv(n, close=110.0, volume=1_000_000.0)
    df.iloc[-1, df.columns.get_loc('Volume')] = 2_500_000.0
    mocks['yf'].return_value.history.return_value = df

    _configure_ta_mocks(
        mocks, n,
        rsi=25.0,                         # +15: RSI < 30
        sma20=100.0,                      # +15: 110 > 100
        macd_val=0.0, macd_sig=1.0,       # -10: MACD < signal
        bb_upper=112.0, bb_lower=90.0, bb_mid=101.0,  # -10: 110>=112-0.2*22=107.6
        adx=30.0, adx_pos=15.0, adx_neg=25.0,         # -10: strong downtrend
        stoch=50.0, stoch_signal=50.0,                 #   0: neutral
        vwap=120.0,                       # -10: 110 ≤ 120
        ichi_a=105.0, ichi_b=103.0,       # +10: 110 > cloud_top(105)
    )

    response = client.get('/api/stock/TEST.NS')
    data = json.loads(response.data)

    assert response.status_code == 200
    assert data['score'] == 0
    assert data['signal'] == 'Hold'
    confirm_texts = ' '.join(data['categories']['Confirmation'])
    assert 'no structural bias' in confirm_texts


# ══════════════════════════════════════════════════════════════════════════════
#  WB-09  EMPTY DATAFRAME → 404 Error (Line 31-32)
# ══════════════════════════════════════════════════════════════════════════════

@patch('app.yf.Ticker')
def test_wb09_empty_dataframe(mock_yf, client):
    """Empty DataFrame from yfinance → 404 with error message."""
    mock_yf.return_value.history.return_value = pd.DataFrame()

    response = client.get('/api/stock/INVALID.NS')
    data = json.loads(response.data)

    assert response.status_code == 404
    assert 'error' in data
    assert 'No data found' in data['error']


# ══════════════════════════════════════════════════════════════════════════════
#  WB-10  INSUFFICIENT DATA (1 row) → 400 Error (Line 97-98)
# ══════════════════════════════════════════════════════════════════════════════

@patch(PATCH_STACK[0])
@patch(PATCH_STACK[1])
@patch(PATCH_STACK[2])
@patch(PATCH_STACK[3])
@patch(PATCH_STACK[4])
@patch(PATCH_STACK[5])
@patch(PATCH_STACK[6])
@patch(PATCH_STACK[7])
@patch(PATCH_STACK[8])
def test_wb10_insufficient_data(mock_yf, mock_rsi, mock_sma, mock_macd,
                                mock_bb, mock_adx, mock_stoch, mock_ichi,
                                mock_vwap, client):
    """Only 1 row of data → len(df) < 2 → 400 error."""
    n = 1
    mocks = _unpack_mocks(mock_yf, mock_rsi, mock_sma, mock_macd,
                          mock_bb, mock_adx, mock_stoch, mock_ichi, mock_vwap)

    df = _make_ohlcv(n, close=100.0, volume=1_000_000.0)
    mocks['yf'].return_value.history.return_value = df

    # Configure mocks with length-1 series (only constant values, no prev)
    _configure_ta_mocks(mocks, n=n, rsi=50.0, sma20=100.0)

    response = client.get('/api/stock/TEST.NS')
    data = json.loads(response.data)

    assert response.status_code == 400
    assert 'error' in data
    assert 'Not enough data' in data['error']


# ══════════════════════════════════════════════════════════════════════════════
#  STRUCTURAL TESTS — Response shape & API endpoints
# ══════════════════════════════════════════════════════════════════════════════

def test_get_stocks_endpoint(client):
    """GET /api/stocks returns the pre-populated stock list."""
    response = client.get('/api/stocks')
    data = json.loads(response.data)

    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) > 0
    assert 'ticker' in data[0]
    assert 'name' in data[0]


@patch(PATCH_STACK[0])
@patch(PATCH_STACK[1])
@patch(PATCH_STACK[2])
@patch(PATCH_STACK[3])
@patch(PATCH_STACK[4])
@patch(PATCH_STACK[5])
@patch(PATCH_STACK[6])
@patch(PATCH_STACK[7])
@patch(PATCH_STACK[8])
def test_response_json_structure(mock_yf, mock_rsi, mock_sma, mock_macd,
                                 mock_bb, mock_adx, mock_stoch, mock_ichi,
                                 mock_vwap, client):
    """Validate all required keys exist in a successful response."""
    n = NUM_ROWS
    mocks = _unpack_mocks(mock_yf, mock_rsi, mock_sma, mock_macd,
                          mock_bb, mock_adx, mock_stoch, mock_ichi, mock_vwap)

    df = _make_ohlcv(n, close=100.0, volume=1_000_000.0)
    mocks['yf'].return_value.history.return_value = df
    _configure_ta_mocks(mocks, n)

    response = client.get('/api/stock/TEST.NS')
    data = json.loads(response.data)

    assert response.status_code == 200

    # Top-level keys
    required_keys = ['ticker', 'signal', 'score', 'categories', 'data', 'latest']
    for key in required_keys:
        assert key in data, f"Missing top-level key: {key}"

    # Signal must be one of three values
    assert data['signal'] in ('Buy', 'Sell', 'Hold')

    # Score must be in valid range
    assert -100 <= data['score'] <= 100

    # Categories must have all 4 sub-sections
    for cat in ('Trend', 'Momentum', 'Timing', 'Confirmation'):
        assert cat in data['categories'], f"Missing category: {cat}"
        assert len(data['categories'][cat]) > 0

    # Chart data must be non-empty list of OHLCV dicts
    assert isinstance(data['data'], list)
    assert len(data['data']) > 0
    chart_point = data['data'][0]
    for field in ('time', 'open', 'high', 'low', 'close', 'volume'):
        assert field in chart_point, f"Missing chart field: {field}"

    # Latest snapshot
    assert 'close' in data['latest']
    assert 'rsi' in data['latest']
    assert 'sma20' in data['latest']
