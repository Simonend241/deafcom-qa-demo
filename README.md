# Deafcom QA Automation Demo

Automated E2E testing demo for Deafcom.org using Python, Playwright, and pytest.

## Features
* **Navigation Smoke Test:** Verifies core navigation links and URL routing.
* **Form Validation (Negative Testing):** Asserts UI error rendering for empty inputs and boundary values.
* **Network Interception:** Blocks outbound POST requests during tests to prevent spamming production endpoints.

## AI Usage
To fulfill the assignment requirements, the baseline code was generated using AI based on my specific test scenarios and architecture prompts. The tests were then locally executed and reviewed.

## How to Run
1. Install dependencies: 
   `pip install pytest-playwright`
2. Install Playwright browsers: 
   `playwright install`
3. Execute the test suite: 
   `pytest test_deafcom.py`
