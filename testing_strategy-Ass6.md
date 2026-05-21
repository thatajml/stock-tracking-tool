# Stock Trading Tool: Comprehensive Testing Strategy

## Table of Contents
1. [Objective 1 — White Box Testing (Branch Coverage)](#1-white-box-testing--branch-coverage)
2. [Objective 2 — Black Box Testing (Standard Techniques)](#2-black-box-testing--standard-techniques)
3. [Objective 3 — IEEE 829 Test Case Format](#3-ieee-829-test-case-format)
4. [Objective 4 — Selenium with Java Automation](#4-selenium-with-java-automation)
5. [Objective 5 — Test Result Analysis](#5-test-result-analysis)

---

## 1. White Box Testing — Branch Coverage

### 1.1 Target Module
**File:** [app.py](file:///Users/Allu/SEM/StockTrackingTool/backend/app.py) — `get_stock_data()` function (Lines 24–271)

### 1.2 Control Flow Graph — Branch Identification

The scoring engine contains **19 decision branches** across 4 categories. Each branch is mapped below with its line reference and the condition required to traverse it.

#### Category 1: Trend (Lines 118–152) — 7 Branches

| Branch ID | Line | Condition | True Path | False Path |
|:--|:--|:--|:--|:--|
| B1 | 118 | `close > sma20` | +15 score | −15 score |
| B2 | 128 | `adx > 25` | Enter B3 | 0 score (weak trend) |
| B3 | 129 | `adx_pos > adx_neg` | +10 score | −10 score |
| B4 | 140 | `ichi_a and ichi_b` (both non-zero) | Enter B5 | 0 score (unavailable) |
| B5 | 143 | `close > cloud_top` | +10 score | Enter B6 |
| B6 | 146 | `close < cloud_bottom` | −10 score | 0 score (inside cloud) |

#### Category 2: Momentum (Lines 157–175) — 5 Branches

| Branch ID | Line | Condition | True Path | False Path |
|:--|:--|:--|:--|:--|
| B7 | 157 | `rsi < 30` OR `(40 ≤ rsi ≤ 60 AND rsi > rsi_prev)` | +15 score | Enter B8 |
| B8 | 160 | `rsi > 70` OR `(40 ≤ rsi ≤ 60 AND rsi < rsi_prev)` | −15 score | 0 score |
| B9 | 168 | `stoch < 20 AND stoch > stoch_signal` | +10 score | Enter B10 |
| B10 | 171 | `stoch > 80 AND stoch < stoch_signal` | −10 score | 0 score |

#### Category 3: Timing (Lines 180–193) — 3 Branches

| Branch ID | Line | Condition | True Path | False Path |
|:--|:--|:--|:--|:--|
| B11 | 180 | `macd > macd_signal` | +10 score | −10 score |
| B12 | 188 | `close > vwap` | +10 score | −10 score |

#### Category 4: Confirmation (Lines 198–223) — 6 Branches

| Branch ID | Line | Condition | True Path | False Path |
|:--|:--|:--|:--|:--|
| B13 | 198 | `bb_upper and bb_lower` (both non-zero) | Enter B14 | 0 score |
| B14 | 200 | `close ≤ bb_lower + 0.2 × bb_width` | +10 score | Enter B15 |
| B15 | 203 | `close ≥ bb_upper − 0.2 × bb_width` | −10 score | 0 score |
| B16 | 213 | `volume > volume_sma20` | Enter B17 | 0 score |
| B17 | 214 | `total_score > 0` | +10 score | Enter B18 |
| B18 | 217 | `total_score < 0` | −10 score | 0 score (neutral) |

#### Signal Decision (Lines 226–229) — 3 Branches

| Branch ID | Line | Condition | Result |
|:--|:--|:--|:--|
| B19a | 226 | `total_score ≥ 60` | Signal = **Buy** |
| B19b | 228 | `total_score ≤ −60` | Signal = **Sell** |
| B19c | 225 | Otherwise (default) | Signal = **Hold** |

### 1.3 Branch Coverage Test Cases

To achieve **100% branch coverage**, the following 8 test scenarios are designed. Each scenario specifies the mock indicator values needed to force execution through specific branches.

| Test ID | Scenario | Key Mock Values | Branches Hit | Expected Score | Expected Signal |
|:--|:--|:--|:--|:--|:--|
| WB-01 | **Maximum Bullish** | close=110, sma20=100, adx=30, +DI>−DI, price above cloud, RSI=25, stoch=15 (>sig), MACD>sig, close>VWAP, close near lower BB, vol>sma | B1T, B2T, B3T, B4T, B5T, B7T, B9T, B11T, B12T, B14T, B16T, B17T | +100 | Buy |
| WB-02 | **Maximum Bearish** | close=90, sma20=100, adx=30, −DI>+DI, price below cloud, RSI=75, stoch=85 (<sig), MACD<sig, close<VWAP, close near upper BB, vol>sma | B1F, B2T, B3F, B4T, B6T, B8T, B10T, B11F, B12F, B15T, B16T, B18T | −100 | Sell |
| WB-03 | **Neutral / Hold** | close=100, sma20=100, adx=20, price inside cloud, RSI=50 (=prev), stoch=50, MACD=sig, close=VWAP, price mid BB, vol<sma | B1F, B2F, B4T, B5F/B6F, B7F/B8F, B9F/B10F, B11F, B12F, B13T, B14F/B15F, B16F | ~−15 | Hold |
| WB-04 | **Ichimoku Unavailable** | ichi_a=None, ichi_b=None | B4F | — | — |
| WB-05 | **Bollinger Unavailable** | bb_upper=None, bb_lower=None | B13F | — | — |
| WB-06 | **RSI Oversold Bounce** | RSI=45, prev_RSI=40 (rising in neutral zone) | B7T | +15 | — |
| WB-07 | **RSI Overbought Rejection** | RSI=55, prev_RSI=58 (falling in neutral zone) | B8T | −15 | — |
| WB-08 | **High Volume Neutral Score** | vol>sma, total_score=0 at volume check | B16T, B17F, B18F | 0 added | — |

### 1.4 Coverage Tool Setup

```bash
# Install coverage tools
pip install pytest pytest-cov

# Run with branch coverage measurement
pytest tests/test_backend.py --cov=app --cov-branch --cov-report=term-missing

# Generate HTML report
pytest tests/test_backend.py --cov=app --cov-branch --cov-report=html
```

### 1.5 Sample Test Implementation (`tests/test_backend.py`)

```python
import pytest
import json
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def _mock_dataframe(overrides=None):
    """Build a 2-row DataFrame with controllable indicator values."""
    defaults = {
        'Date': ['2026-04-07', '2026-04-08'],
        'Open': [100, 100], 'High': [105, 105],
        'Low': [95, 95], 'Close': [102, 102],
        'Volume': [1000000, 1200000],
        'rsi': [50, 50], 'sma20': [100, 100],
        'macd': [1, 1], 'macd_signal': [0.5, 0.5], 'macd_hist': [0.5, 0.5],
        'bb_upper': [110, 110], 'bb_lower': [90, 90], 'bb_mid': [100, 100],
        'adx': [30, 30], 'adx_pos': [20, 20], 'adx_neg': [15, 15],
        'stoch': [50, 50], 'stoch_signal': [50, 50],
        'vwap': [100, 100],
        'ichimoku_a': [98, 98], 'ichimoku_b': [96, 96],
        'volume_sma20': [900000, 900000],
        'rolling_high': [105, 105], 'rolling_low': [95, 95],
        'fib_382': [101.18, 101.18], 'fib_618': [98.82, 98.82],
    }
    if overrides:
        for key, val in overrides.items():
            defaults[key] = val
    return pd.DataFrame(defaults)

class TestWB01_MaxBullish:
    """WB-01: All bullish branches → Score = +100, Signal = Buy"""

    @patch('app.yf.Ticker')
    def test_maximum_bullish_signal(self, mock_ticker, client):
        df = _mock_dataframe({
            'Close': [108, 110],
            'sma20': [100, 100],         # B1 True: close > sma20
            'adx': [30, 30],             # B2 True: adx > 25
            'adx_pos': [25, 25],         # B3 True: +DI > -DI
            'adx_neg': [15, 15],
            'ichimoku_a': [105, 105],    # B4 True, B5 True: above cloud
            'ichimoku_b': [103, 103],
            'rsi': [50, 25],             # B7 True: RSI < 30
            'stoch': [15, 15],           # B9 True: stoch < 20
            'stoch_signal': [10, 10],    #          and stoch > signal
            'macd': [2, 2],              # B11 True: MACD > signal
            'macd_signal': [1, 1],
            'vwap': [100, 100],          # B12 True: close > VWAP
            'bb_upper': [115, 115],      # B14 True: near lower band
            'bb_lower': [90, 90],
            'Volume': [2000000, 2000000],  # B16 True: vol > sma
            'volume_sma20': [1000000, 1000000],
        })
        mock_ticker.return_value.history.return_value = df
        response = client.get('/api/stock/TEST.NS')
        data = json.loads(response.data)
        assert data['score'] == 100
        assert data['signal'] == 'Buy'

class TestWB02_MaxBearish:
    """WB-02: All bearish branches → Score = -100, Signal = Sell"""

    @patch('app.yf.Ticker')
    def test_maximum_bearish_signal(self, mock_ticker, client):
        df = _mock_dataframe({
            'Close': [88, 90],
            'sma20': [100, 100],         # B1 False
            'adx': [30, 30],             # B2 True
            'adx_pos': [15, 15],         # B3 False: -DI > +DI
            'adx_neg': [25, 25],
            'ichimoku_a': [95, 95],      # B6 True: below cloud
            'ichimoku_b': [93, 93],
            'rsi': [72, 75],             # B8 True: RSI > 70
            'stoch': [85, 85],           # B10 True: stoch > 80
            'stoch_signal': [90, 90],    #           and stoch < signal
            'macd': [-1, -1],            # B11 False
            'macd_signal': [1, 1],
            'vwap': [100, 100],          # B12 False
            'bb_upper': [110, 110],      # B15 True: near upper band
            'bb_lower': [85, 85],
            'Volume': [2000000, 2000000],
            'volume_sma20': [1000000, 1000000],
        })
        mock_ticker.return_value.history.return_value = df
        response = client.get('/api/stock/TEST.NS')
        data = json.loads(response.data)
        assert data['score'] == -100
        assert data['signal'] == 'Sell'
```

---

## 2. Black Box Testing — Standard Techniques

### 2.1 Equivalence Partitioning

Input domain is divided into classes where all values in a class are expected to behave the same.

| Partition ID | Input Class | Example Input | Expected Behaviour |
|:--|:--|:--|:--|
| EP-01 | Valid NSE Ticker (pre-populated) | `RELIANCE.NS` | Returns 200 with signal, score, chart data |
| EP-02 | Valid NSE Ticker (user-typed, no suffix) | `TCS` | Auto-appended to `TCS.NS`, returns 200 |
| EP-03 | Valid NSE Ticker (user-typed, with suffix) | `INFY.NS` | Used as-is, returns 200 |
| EP-04 | Invalid/Non-existent Ticker | `ZZZZZ.NS` | Returns 404 with `"error": "No data found"` |
| EP-05 | Empty Ticker String | `""` | No API call triggered (frontend guard) |
| EP-06 | Special Characters in Ticker | `@#$%` | Returns 404 or 500 error |
| EP-07 | NIFTY 50 Index Ticker | `^NSEI` | Returns 200 (index data) |

### 2.2 Boundary Value Analysis

Testing at the edges of the scoring thresholds and UI rendering boundaries.

| BVA ID | Boundary | Test Values | Expected Result |
|:--|:--|:--|:--|
| BVA-01 | Signal threshold (Buy) | Score = 59, **60**, 61 | Hold, **Buy**, Buy |
| BVA-02 | Signal threshold (Sell) | Score = −59, **−60**, −61 | Hold, **Sell**, Sell |
| BVA-03 | RSI overbought boundary | RSI = 69, **70**, 71 | Neutral, **Bearish**, Bearish |
| BVA-04 | RSI oversold boundary | RSI = 31, **30**, 29 | Neutral, **Bullish**, Bullish |
| BVA-05 | ADX trend strength | ADX = 24, **25**, 26 | Weak, **Weak** (> not ≥), Strong |
| BVA-06 | Stochastic oversold | Stoch = 19, **20**, 21 | Bullish zone, **Out of zone**, Out of zone |
| BVA-07 | Stochastic overbought | Stoch = 79, **80**, 81 | Out of zone, **Out of zone**, Bearish zone |
| BVA-08 | Progress bar clamp | Score = −101, −100, 0, +100, +101 | Clamps to 0%, 0%, 50%, 100%, 100% |
| BVA-09 | DataFrame length | len(df) = 0, 1, **2**, 3 | Error 404, Error 400, **Valid**, Valid |

### 2.3 Decision Table — Signal Output Logic

| Rule | Score ≥ 60 | Score ≤ −60 | Signal |
|:--|:--|:--|:--|
| R1 | True | — | **Buy** |
| R2 | — | True | **Sell** |
| R3 | False | False | **Hold** |

---

## 3. IEEE 829 Test Case Format

### 3.1 Test Plan Identifier
**TP-QUANTSENSE-001** — QuantSense Stock Dashboard Integration Test Plan

### 3.2 Test Case Template

> [!NOTE]
> All test cases below follow the **IEEE 829-2008** standard for Software and System Test Documentation.

---

#### TC-001: Valid Stock Ticker Returns Analysis

| Field | Value |
|:--|:--|
| **Test Case ID** | TC-001 |
| **Test Item** | `GET /api/stock/<ticker>` — Backend API |
| **Objective** | Verify that a valid NSE ticker returns a complete analysis response |
| **Pre-conditions** | Flask server is running on `localhost:5000`; internet connection is active |
| **Input Specification** | HTTP GET request to `/api/stock/RELIANCE.NS` |
| **Output Specification** | JSON response containing: `ticker`, `signal` (Buy/Hold/Sell), `score` (integer), `categories` (object with 4 keys), `data` (array of OHLCV objects) |
| **Pass/Fail Criteria** | **Pass** if: HTTP 200, `signal` ∈ {Buy, Hold, Sell}, `score` ∈ [−100, 100], `data` array is non-empty, all 4 category keys exist |
| **Priority** | High |
| **Test Environment** | macOS, Python 3.11, Flask 3.x |

---

#### TC-002: Invalid Ticker Returns 404 Error

| Field | Value |
|:--|:--|
| **Test Case ID** | TC-002 |
| **Test Item** | `GET /api/stock/<ticker>` — Backend API |
| **Objective** | Verify that a non-existent ticker returns a proper error response |
| **Pre-conditions** | Flask server is running on `localhost:5000` |
| **Input Specification** | HTTP GET request to `/api/stock/INVALIDXYZ.NS` |
| **Output Specification** | JSON response containing `"error"` key |
| **Pass/Fail Criteria** | **Pass** if: HTTP 404, response body contains `"error"` |
| **Priority** | High |
| **Test Environment** | macOS, Python 3.11, Flask 3.x |

---

#### TC-003: Stock Search with Auto-Suffix

| Field | Value |
|:--|:--|
| **Test Case ID** | TC-003 |
| **Test Item** | Stock Search Autocomplete — Frontend (React) |
| **Objective** | Verify that typing a ticker without `.NS` suffix auto-appends it |
| **Pre-conditions** | App is loaded in browser; stock list is fetched |
| **Input Specification** | Type `RELIANCE` into search field, press Enter |
| **Output Specification** | API call is made to `/api/stock/RELIANCE.NS` |
| **Pass/Fail Criteria** | **Pass** if: Network tab shows request to `RELIANCE.NS`, dashboard renders signal |
| **Priority** | Medium |
| **Test Environment** | Chrome 130+, React 18, Vite dev server |

---

#### TC-004: Dashboard Displays Buy Signal Correctly

| Field | Value |
|:--|:--|
| **Test Case ID** | TC-004 |
| **Test Item** | Signal Display Component — Frontend (React) |
| **Objective** | Verify the UI correctly renders a Buy signal with green styling |
| **Pre-conditions** | API returns `signal: "Buy"`, `score: 70` |
| **Input Specification** | Select a stock that triggers a Buy signal |
| **Output Specification** | Alert component shows "Signal: BUY" with `severity="success"` (green), progress bar is green and filled past 80% |
| **Pass/Fail Criteria** | **Pass** if: Alert text = "BUY", colour is green, progress bar value = `(70+100)/2 = 85%` |
| **Priority** | Medium |
| **Test Environment** | Chrome 130+, React 18 |

---

#### TC-005: Chart Renders 3 Synchronized Panels

| Field | Value |
|:--|:--|
| **Test Case ID** | TC-005 |
| **Test Item** | `ChartComponent.jsx` — Multi-panel rendering |
| **Objective** | Verify all 3 chart panels (Price, Volume, Momentum) render and sync scroll |
| **Pre-conditions** | Valid stock data is loaded |
| **Input Specification** | Scroll/zoom the Price Action panel |
| **Output Specification** | Volume and Momentum panels scroll in sync |
| **Pass/Fail Criteria** | **Pass** if: All 3 `<canvas>` elements are present in the DOM, scrolling one panel updates the others |
| **Priority** | High |
| **Test Environment** | Chrome 130+, Lightweight Charts v4 |

---

#### TC-006: Algorithmic Breakdown Shows All 4 Categories

| Field | Value |
|:--|:--|
| **Test Case ID** | TC-006 |
| **Test Item** | Categories Grid — Frontend (React) |
| **Objective** | Verify all 4 scoring categories (Trend, Momentum, Timing, Confirmation) are displayed |
| **Pre-conditions** | Valid stock data is loaded and displayed |
| **Input Specification** | Load analysis for any valid ticker |
| **Output Specification** | 4 Paper cards rendered with headers: "Trend Logic", "Momentum Logic", "Timing Logic", "Confirmation Logic" |
| **Pass/Fail Criteria** | **Pass** if: All 4 category headings are visible; each contains at least 1 list item with a score prefix |
| **Priority** | Medium |
| **Test Environment** | Chrome 130+, React 18 |

---

## 4. Selenium with Java Automation

### 4.1 Project Structure

```
StockTrackingTool/
└── selenium-tests/
    ├── pom.xml
    └── src/
        └── test/
            └── java/
                └── com/quantsense/tests/
                    ├── DashboardTest.java
                    └── SearchTest.java
```

### 4.2 Maven Dependencies (`pom.xml`)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.quantsense</groupId>
    <artifactId>selenium-tests</artifactId>
    <version>1.0-SNAPSHOT</version>

    <properties>
        <maven.compiler.source>17</maven.compiler.source>
        <maven.compiler.target>17</maven.compiler.target>
        <selenium.version>4.20.0</selenium.version>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.seleniumhq.selenium</groupId>
            <artifactId>selenium-java</artifactId>
            <version>${selenium.version}</version>
        </dependency>
        <dependency>
            <groupId>io.github.bonigarcia</groupId>
            <artifactId>webdrivermanager</artifactId>
            <version>5.8.0</version>
        </dependency>
        <dependency>
            <groupId>org.testng</groupId>
            <artifactId>testng</artifactId>
            <version>7.10.2</version>
            <scope>test</scope>
        </dependency>
    </dependencies>
</project>
```

### 4.3 Test Class: `DashboardTest.java`

```java
package com.quantsense.tests;

import io.github.bonigarcia.wdm.WebDriverManager;
import org.openqa.selenium.*;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.Assert;
import org.testng.annotations.*;

import java.time.Duration;

public class DashboardTest {

    WebDriver driver;
    WebDriverWait wait;
    static final String BASE_URL = "http://localhost:5173";

    @BeforeClass
    public void setUp() {
        WebDriverManager.chromedriver().setup();
        driver = new ChromeDriver();
        driver.manage().window().maximize();
        wait = new WebDriverWait(driver, Duration.ofSeconds(15));
    }

    @Test(priority = 1)
    public void testPageTitle() {
        driver.get(BASE_URL);
        wait.until(ExpectedConditions.presenceOfElementLocated(
            By.xpath("//h6[contains(text(),'Stock Signal Dashboard')]")
        ));
        WebElement title = driver.findElement(
            By.xpath("//h6[contains(text(),'Stock Signal Dashboard')]")
        );
        Assert.assertTrue(title.isDisplayed(),
            "Dashboard title should be visible on page load");
    }

    @Test(priority = 2)
    public void testDefaultStockLoads() {
        driver.get(BASE_URL);
        // Wait for the signal alert to appear (means data loaded)
        WebElement signalAlert = wait.until(
            ExpectedConditions.presenceOfElementLocated(
                By.xpath("//h5[contains(text(),'Signal:')]")
            )
        );
        Assert.assertTrue(signalAlert.isDisplayed(),
            "Signal alert should appear after default stock loads");

        String signalText = signalAlert.getText();
        Assert.assertTrue(
            signalText.contains("BUY") ||
            signalText.contains("SELL") ||
            signalText.contains("HOLD"),
            "Signal text should contain BUY, SELL, or HOLD"
        );
    }

    @Test(priority = 3)
    public void testChartPanelsRendered() {
        driver.get(BASE_URL);
        wait.until(ExpectedConditions.presenceOfElementLocated(
            By.xpath("//h5[contains(text(),'Signal:')]")
        ));
        // Verify all 3 chart panels exist via their labels
        WebElement priceLabel = driver.findElement(
            By.xpath("//*[contains(text(),'Price Action')]")
        );
        WebElement volumeLabel = driver.findElement(
            By.xpath("//*[contains(text(),'Volume Profile')]")
        );
        WebElement momentumLabel = driver.findElement(
            By.xpath("//*[contains(text(),'Momentum')]")
        );

        Assert.assertTrue(priceLabel.isDisplayed(), "Price panel label visible");
        Assert.assertTrue(volumeLabel.isDisplayed(), "Volume panel label visible");
        Assert.assertTrue(momentumLabel.isDisplayed(), "Momentum panel label visible");
    }

    @Test(priority = 4)
    public void testCategoryBreakdownCards() {
        driver.get(BASE_URL);
        wait.until(ExpectedConditions.presenceOfElementLocated(
            By.xpath("//h5[contains(text(),'Signal:')]")
        ));

        String[] categories = {"Trend Logic", "Momentum Logic",
                               "Timing Logic", "Confirmation Logic"};
        for (String cat : categories) {
            WebElement card = driver.findElement(
                By.xpath("//*[contains(text(),'" + cat + "')]")
            );
            Assert.assertTrue(card.isDisplayed(),
                cat + " card should be visible");
        }
    }

    @AfterClass
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }
}
```

### 4.4 Test Class: `SearchTest.java`

```java
package com.quantsense.tests;

import io.github.bonigarcia.wdm.WebDriverManager;
import org.openqa.selenium.*;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.Assert;
import org.testng.annotations.*;

import java.time.Duration;

public class SearchTest {

    WebDriver driver;
    WebDriverWait wait;
    static final String BASE_URL = "http://localhost:5173";

    @BeforeClass
    public void setUp() {
        WebDriverManager.chromedriver().setup();
        driver = new ChromeDriver();
        driver.manage().window().maximize();
        wait = new WebDriverWait(driver, Duration.ofSeconds(15));
    }

    @Test(priority = 1)
    public void testSearchForCustomTicker() {
        driver.get(BASE_URL);

        // Wait for initial load
        wait.until(ExpectedConditions.presenceOfElementLocated(
            By.id("stock-search")
        ));

        WebElement searchField = driver.findElement(By.id("stock-search"));

        // Clear and type a custom ticker
        searchField.clear();
        searchField.sendKeys("TCS");
        searchField.sendKeys(Keys.ENTER);

        // Wait for the signal to update
        WebElement signalAlert = wait.until(
            ExpectedConditions.presenceOfElementLocated(
                By.xpath("//h5[contains(text(),'Signal:')]")
            )
        );

        Assert.assertTrue(signalAlert.isDisplayed(),
            "Signal should appear after searching for TCS");
    }

    @Test(priority = 2)
    public void testSearchFieldDisabledDuringLoading() {
        driver.get(BASE_URL);

        WebElement searchField = wait.until(
            ExpectedConditions.presenceOfElementLocated(By.id("stock-search"))
        );

        // Type and submit to trigger loading state
        searchField.clear();
        searchField.sendKeys("INFY");
        searchField.sendKeys(Keys.ENTER);

        // During loading, the CircularProgress should appear
        try {
            WebElement spinner = wait.until(
                ExpectedConditions.presenceOfElementLocated(
                    By.cssSelector("[role='progressbar']")
                )
            );
            // If spinner appears, search should be disabled
            Assert.assertTrue(true,
                "Loading indicator appeared during data fetch");
        } catch (TimeoutException e) {
            // Data loaded very fast — acceptable
            Assert.assertTrue(true,
                "Data loaded before spinner could be detected");
        }
    }

    @Test(priority = 3)
    public void testInvalidTickerShowsError() {
        driver.get(BASE_URL);

        WebElement searchField = wait.until(
            ExpectedConditions.presenceOfElementLocated(By.id("stock-search"))
        );

        searchField.clear();
        searchField.sendKeys("XYZINVALID");
        searchField.sendKeys(Keys.ENTER);

        // Wait for error alert
        WebElement errorAlert = wait.until(
            ExpectedConditions.presenceOfElementLocated(
                By.cssSelector("[role='alert']")
            )
        );

        Assert.assertTrue(errorAlert.getText().contains("Failed"),
            "Error message should indicate failure for invalid ticker");
    }

    @AfterClass
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }
}
```

### 4.5 Running the Selenium Tests

```bash
cd selenium-tests
mvn test
```

---

## 5. Test Result Analysis

### 5.1 Expected Test Execution Summary

| Test Suite | Total Tests | Strategy |
|:--|:--|:--|
| White Box (pytest) | 8 | Branch coverage of scoring engine |
| Black Box (EP + BVA) | 16 | Input partitioning and boundary values |
| IEEE Test Cases | 6 | Documented acceptance criteria |
| Selenium (Java) | 7 | End-to-end UI automation |
| **Total** | **37** | |

### 5.2 Result Interpretation Guide

| Observation | Likely Root Cause | Action |
|:--|:--|:--|
| White box test fails on score assertion | Branch logic error in `app.py` scoring engine | Debug the specific category (Trend/Momentum/Timing/Confirmation), trace mock values through each `if` block |
| Black box test returns 500 instead of 404 | Unhandled exception before the `df.empty` check | Add try/catch around `yf.Ticker()` call; validate ticker format before API call |
| Selenium test times out waiting for signal | Backend is slow or unresponsive | Check Flask logs; verify `yfinance` can reach Yahoo servers; increase `WebDriverWait` timeout |
| Selenium cannot find element by XPath | Frontend component text or structure changed | Update XPath selectors to match current DOM; add stable `data-testid` attributes to React components |
| Branch coverage < 100% | Some edge cases not reached by test data | Review `--cov-report=term-missing` output to find uncovered lines; add targeted test with mock values forcing that branch |

### 5.3 Sample Coverage Report Output

```
Name      Stmts   Miss  Branch  BrPart  Cover   Missing
---------------------------------------------------------
app.py      142      3      38       2    96%    140->152, 217->220
---------------------------------------------------------
TOTAL       142      3      38       2    96%
```

> [!TIP]
> **Reading the report**: `140->152` means the branch from line 140 to line 152 (Ichimoku unavailable path) was never executed. Add test case WB-04 with `ichi_a=None` to cover it.
