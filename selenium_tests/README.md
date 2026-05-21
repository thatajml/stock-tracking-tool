# QuantSense — Selenium Test Suite

## Prerequisites

1. **Chrome browser** installed
2. **Backend running** on `http://127.0.0.1:5000`
3. **Frontend running** on `http://localhost:5173`

## Setup

```bash
# From the project root
cd selenium_tests

# Install dependencies (use your conda/venv environment)
pip install -r requirements.txt
```

## Run All Tests

```bash
# Run all tests with verbose output
pytest -v

# Run with detailed print output
pytest -v -s
```

## Run Specific Test Files

```bash
# Dashboard UI tests only
pytest test_dashboard.py -v

# Search & navigation tests only
pytest test_search.py -v

# Responsiveness tests only
pytest test_responsiveness.py -v
```

## Run in Headless Mode (no browser window)

Uncomment the `--headless=new` line in `conftest.py`:

```python
chrome_options.add_argument("--headless=new")
```

## Screenshots on Failure

Failed tests automatically capture screenshots to the `screenshots/` directory.

## Test Coverage Summary

| File                     | Tests | Covers                                          |
|:-------------------------|:------|:------------------------------------------------|
| `test_dashboard.py`      | 14    | Page structure, signal display, charts, categories |
| `test_search.py`         | 5     | Custom ticker, dropdown, invalid input, loading  |
| `test_responsiveness.py` | 5     | Viewport sizes, JS errors, scrolling             |
| **Total**                | **24** |                                                 |
