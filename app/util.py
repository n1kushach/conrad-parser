from playwright.sync_api import Error as PlaywrightTimeoutError


def optional_text(page, css, timeout=3000):
    try:
        return " ".join(page.locator(css).first.inner_text(timeout=timeout).split())
    except PlaywrightTimeoutError:
        return None
