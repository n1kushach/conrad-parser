from loguru import logger
from playwright.sync_api import (
    Error as PlaywrightError,
)
from playwright.sync_api import (
    TimeoutError as PlaywrightTimeoutError,
)

from app.config import NAVIGATION_TIMEOUT


def click_if_present(page, name=None, css=None, timeout=5000, sleep_after=2):
    """Click the first visible button (by name) or element (by CSS), if present."""
    label = name or css

    target = page.locator(css) if css else page.get_by_role("button", name=name)

    try:
        target = target.locator("visible=true").first
        target.click(timeout=timeout)

        logger.info(f"Clicked {label!r}")
        page.wait_for_timeout(sleep_after * 1000)
        return True

    except PlaywrightTimeoutError:
        logger.warning(f"Could not click {label!r}")
        return False


def navigate(page, url):
    """Navigate while handling interrupted navigation."""
    try:
        logger.info(f"Navigating to {url}")
        page.goto(url, wait_until="domcontentloaded", timeout=NAVIGATION_TIMEOUT)
    except PlaywrightError as e:
        logger.warning(f"Navigation warning: {e}")
        # Check whether navigation actually succeeded.
        logger.warning(f"Current URL: {page.url}")

    page.wait_for_timeout(3000)


def login(page, email, password):
    try:
        logger.info("Logging in...")
        page.get_by_label("E-Mail").fill(email)
        page.locator('[data-test-button="next"]').click()
        password_input = page.locator('[data-test-input="password"]')
        password_input.wait_for(
            state="visible",
            timeout=15000,
        )
        password_input.fill(password)
        page.locator('[data-faro-user-action-name="password-submit"]').click()
        page.wait_for_timeout(5000)
        logger.success(f"Login flow completed. Current URL: {page.url}")
    except PlaywrightTimeoutError as e:
        logger.warning(f"There is an error - {e}")
