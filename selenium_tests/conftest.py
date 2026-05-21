"""
Selenium Test Configuration for QuantSense Stock Tracking Tool.

Provides shared fixtures for all Selenium test modules:
- WebDriver setup/teardown
- Common wait utilities
- Screenshot capture on failure
"""

import pytest
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait


# ──────────────────────────────────────────────
# Configuration Constants
# ──────────────────────────────────────────────
FRONTEND_URL = "http://localhost:5173"
BACKEND_URL = "http://127.0.0.1:5000"
DEFAULT_WAIT_SECONDS = 20  # yfinance can be slow

SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


# ──────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────
@pytest.fixture(scope="session")
def driver():
    """Session-scoped Chrome WebDriver."""
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    
    chrome_options = Options()
    chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1440,900")

    os.environ['WDM_LOCAL'] = '1'
    
    browser = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    browser.implicitly_wait(5)

    yield browser

    browser.quit()


@pytest.fixture(scope="session")
def wait(driver):
    """Reusable explicit wait object with default timeout."""
    return WebDriverWait(driver, DEFAULT_WAIT_SECONDS)


@pytest.fixture(autouse=True)
def screenshot_on_failure(request, driver):
    """Automatically capture a screenshot when a test fails."""
    yield
    rep = getattr(request.node, "rep_call", None)
    if rep and rep.failed:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_name = request.node.name
        filepath = os.path.join(SCREENSHOT_DIR, f"FAIL_{test_name}_{timestamp}.png")
        driver.save_screenshot(filepath)
        print(f"\n📸 Screenshot saved: {filepath}")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attach test result to the request node for screenshot_on_failure."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
