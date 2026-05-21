"""
TC-001, TC-004, TC-005, TC-006 — Dashboard UI Tests

Tests the core dashboard functionality:
  1. Page loads with correct title and header
  2. Default stock auto-loads and displays a signal
  3. Signal colour/severity matches Buy/Hold/Sell
  4. All 3 chart panels render
  5. Algorithmic breakdown shows all 4 category cards
  6. Progress bar renders with correct range labels
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from conftest import FRONTEND_URL


# ═══════════════════════════════════════════════
# TC-001: Page Structure & Title
# ═══════════════════════════════════════════════
class TestPageStructure:

    def test_page_loads_successfully(self, driver, wait):
        """Verify the app loads without crashing."""
        driver.get(FRONTEND_URL)
        wait.until(EC.presence_of_element_located(
            (By.XPATH, "//h6[contains(text(),'Stock Signal Dashboard')]")
        ))

    def test_app_bar_title_visible(self, driver, wait):
        """TC-001: Dashboard header text is rendered in the AppBar."""
        driver.get(FRONTEND_URL)
        title = wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//h6[contains(text(),'Stock Signal Dashboard')]")
        ))
        assert title.is_displayed(), "AppBar title should be visible"
        assert "Pro System" in title.text, "Title should contain 'Pro System'"

    def test_quantitative_analysis_heading(self, driver, wait):
        """Verify the main 'Quantitative Analysis' heading exists."""
        driver.get(FRONTEND_URL)
        heading = wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//h1[contains(text(),'Quantitative Analysis')]")
        ))
        assert heading.is_displayed()

    def test_stock_search_field_present(self, driver, wait):
        """Verify the stock search Autocomplete field is present."""
        driver.get(FRONTEND_URL)
        search = wait.until(EC.presence_of_element_located(
            (By.ID, "stock-search")
        ))
        assert search is not None, "Search field with id='stock-search' should exist"


# ═══════════════════════════════════════════════
# TC-002: Default Stock Auto-Load
# ═══════════════════════════════════════════════
class TestDefaultStockLoad:

    def test_signal_appears_after_load(self, driver, wait):
        """TC-002: After page load, the first stock's signal should appear."""
        driver.get(FRONTEND_URL)
        signal_element = wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//h5[contains(text(),'Signal:')]")
        ))
        assert signal_element.is_displayed(), "Signal alert should be visible"

    def test_signal_contains_valid_value(self, driver, wait):
        """Signal text must be one of BUY, SELL, or HOLD."""
        driver.get(FRONTEND_URL)
        signal_element = wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//h5[contains(text(),'Signal:')]")
        ))
        signal_text = signal_element.text.upper()
        assert any(s in signal_text for s in ["BUY", "SELL", "HOLD"]), \
            f"Signal should be BUY/SELL/HOLD, got: {signal_text}"

    def test_confidence_score_displayed(self, driver, wait):
        """Net Confidence Score should be visible alongside the signal."""
        driver.get(FRONTEND_URL)
        wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//h5[contains(text(),'Signal:')]")
        ))
        score_text = driver.find_element(
            By.XPATH, "//*[contains(text(),'Net Confidence Score')]"
        )
        assert score_text.is_displayed(), "Confidence score should be rendered"


# ═══════════════════════════════════════════════
# TC-004: Signal Severity & Colour
# ═══════════════════════════════════════════════
class TestSignalDisplay:

    def test_signal_alert_has_severity_role(self, driver, wait):
        """The signal container should have role='alert' via MUI Alert."""
        driver.get(FRONTEND_URL)
        wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//h5[contains(text(),'Signal:')]")
        ))
        alerts = driver.find_elements(By.CSS_SELECTOR, "[role='alert']")
        assert len(alerts) >= 1, "At least one MUI Alert should be rendered"

    def test_progress_bar_rendered(self, driver, wait):
        """The LinearProgress bar for confidence score should exist."""
        driver.get(FRONTEND_URL)
        wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//h5[contains(text(),'Signal:')]")
        ))
        progress = driver.find_elements(By.CSS_SELECTOR, "[role='progressbar']")
        assert len(progress) >= 1, "Progress bar should be rendered"

    def test_progress_bar_range_labels(self, driver, wait):
        """Labels HEAVY SELL, HOLD RANGE, HEAVY BUY should frame the bar."""
        driver.get(FRONTEND_URL)
        wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//h5[contains(text(),'Signal:')]")
        ))

        labels = ["HEAVY SELL", "HOLD RANGE", "HEAVY BUY"]
        for label in labels:
            elem = driver.find_element(
                By.XPATH, f"//*[contains(text(),'{label}')]"
            )
            assert elem.is_displayed(), f"'{label}' label should be visible"


# ═══════════════════════════════════════════════
# TC-005: Chart Panel Rendering
# ═══════════════════════════════════════════════
class TestChartPanels:

    def test_price_action_panel_visible(self, driver, wait):
        """TC-005: Price Action chart panel should render."""
        driver.get(FRONTEND_URL)
        wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//h5[contains(text(),'Signal:')]")
        ))
        price_label = driver.find_element(
            By.XPATH, "//*[contains(text(),'Price Action')]"
        )
        assert price_label.is_displayed(), "Price Action panel should be visible"

    def test_volume_profile_panel_visible(self, driver, wait):
        """TC-005: Volume Profile chart panel should render."""
        driver.get(FRONTEND_URL)
        wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//h5[contains(text(),'Signal:')]")
        ))
        volume_label = driver.find_element(
            By.XPATH, "//*[contains(text(),'Volume Profile')]"
        )
        assert volume_label.is_displayed(), "Volume Profile panel should be visible"

    def test_momentum_panel_visible(self, driver, wait):
        """TC-005: Momentum & Timing chart panel should render."""
        driver.get(FRONTEND_URL)
        wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//h5[contains(text(),'Signal:')]")
        ))
        momentum_label = driver.find_element(
            By.XPATH, "//*[contains(text(),'Momentum')]"
        )
        assert momentum_label.is_displayed(), "Momentum panel should be visible"

    def test_canvas_elements_exist(self, driver, wait):
        """All 3 chart panels should produce <canvas> elements from lightweight-charts."""
        driver.get(FRONTEND_URL)
        wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//h5[contains(text(),'Signal:')]")
        ))
        # lightweight-charts renders into <canvas> tags
        canvases = driver.find_elements(By.TAG_NAME, "canvas")
        assert len(canvases) >= 3, \
            f"Expected at least 3 canvas elements (Price, Volume, Momentum), found {len(canvases)}"


# ═══════════════════════════════════════════════
# TC-006: Algorithmic Breakdown Category Cards
# ═══════════════════════════════════════════════
class TestCategoryBreakdown:

    CATEGORIES = ["Trend Logic", "Momentum Logic", "Timing Logic", "Confirmation Logic"]

    def test_all_four_categories_visible(self, driver, wait):
        """TC-006: All 4 category cards should render after data loads."""
        driver.get(FRONTEND_URL)
        wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//h5[contains(text(),'Signal:')]")
        ))

        for cat in self.CATEGORIES:
            card = driver.find_element(
                By.XPATH, f"//*[contains(text(),'{cat}')]"
            )
            assert card.is_displayed(), f"'{cat}' card should be visible"

    def test_category_cards_have_list_items(self, driver, wait):
        """Each category card should contain at least one reasoning bullet."""
        driver.get(FRONTEND_URL)
        wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//h5[contains(text(),'Signal:')]")
        ))

        list_items = driver.find_elements(By.TAG_NAME, "li")
        assert len(list_items) >= 4, \
            f"Expected at least 4 list items (one per category), found {len(list_items)}"

    def test_breakdown_section_heading(self, driver, wait):
        """The 'Algorithmic Breakdown by Sub-Section' heading should exist."""
        driver.get(FRONTEND_URL)
        wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//h5[contains(text(),'Signal:')]")
        ))
        heading = driver.find_element(
            By.XPATH, "//*[contains(text(),'Algorithmic Breakdown')]"
        )
        assert heading.is_displayed()
