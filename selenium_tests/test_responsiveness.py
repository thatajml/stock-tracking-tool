"""
UI Responsiveness & Cross-Browser Tests

Tests visual/layout aspects of the dashboard:
  1. Responsive layout at different viewport widths
  2. No JavaScript console errors on page load
  3. Historical Price & Volume paper card renders
  4. Scroll behaviour — all sections are reachable
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from conftest import FRONTEND_URL


class TestResponsiveLayout:

    def test_desktop_layout_1440(self, driver, wait):
        """Dashboard renders correctly at 1440px (desktop) width."""
        driver.set_window_size(1440, 900)
        driver.get(FRONTEND_URL)

        wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//h5[contains(text(),'Signal:')]")
        ))

        # Category cards should be in a 2-column grid (md=6 → 2 per row)
        categories = driver.find_elements(
            By.XPATH, "//*[contains(text(),'Logic')]"
        )
        assert len(categories) >= 4, "All 4 category cards should render at desktop width"

    def test_tablet_layout_768(self, driver, wait):
        """Dashboard adapts to 768px (tablet) width without overflow."""
        driver.set_window_size(768, 1024)
        driver.get(FRONTEND_URL)

        wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//h5[contains(text(),'Signal:')]")
        ))

        # App should still render — no crash
        body_width = driver.execute_script("return document.body.scrollWidth")
        viewport_width = driver.execute_script("return window.innerWidth")

        # Allow slight overflow (scrollbar, etc) but no major horizontal overflow
        assert body_width <= viewport_width + 50, \
            f"Page should not overflow horizontally: body={body_width}, viewport={viewport_width}"

    def test_mobile_layout_375(self, driver, wait):
        """Dashboard renders without crash at 375px (iPhone) width."""
        driver.set_window_size(375, 812)
        driver.get(FRONTEND_URL)

        # Just verify the page loads and the AppBar is visible
        title = wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//h6[contains(text(),'Stock Signal Dashboard')]")
        ))
        assert title.is_displayed(), "App should still render at mobile width"

        # Restore desktop size for subsequent tests
        driver.set_window_size(1440, 900)


class TestNoJavaScriptErrors:

    def test_no_console_errors_on_load(self, driver, wait):
        """No critical JS errors should appear in the browser console on load."""
        driver.get(FRONTEND_URL)

        wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//h5[contains(text(),'Signal:')]")
        ))

        # Get browser console logs (Chrome only)
        logs = driver.get_log("browser")
        severe_errors = [
            log for log in logs
            if log["level"] == "SEVERE"
            and "favicon" not in log["message"].lower()
        ]
        # Print errors for debugging (won't fail test on warnings)
        for err in severe_errors:
            print(f"  ⚠️ Console SEVERE: {err['message']}")

        assert len(severe_errors) == 0, \
            f"Found {len(severe_errors)} SEVERE console errors: {severe_errors}"


class TestScrollAndSections:

    def test_historical_price_paper_visible(self, driver, wait):
        """The 'Historical Price & Volume' paper card should render."""
        driver.get(FRONTEND_URL)
        wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//h5[contains(text(),'Signal:')]")
        ))

        paper_title = driver.find_element(
            By.XPATH, "//*[contains(text(),'Historical Price')]"
        )
        assert paper_title.is_displayed()

    def test_all_sections_scrollable(self, driver, wait):
        """All major sections should be reachable by scrolling."""
        driver.set_window_size(1440, 900)
        driver.get(FRONTEND_URL)
        wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//h5[contains(text(),'Signal:')]")
        ))

        # Scroll to the bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")

        # After scrolling, the "Confirmation Logic" card (last category) should
        # be in the viewport or at least present in the DOM
        confirmation = driver.find_element(
            By.XPATH, "//*[contains(text(),'Confirmation Logic')]"
        )
        assert confirmation is not None, \
            "Confirmation Logic card should exist and be reachable by scrolling"
