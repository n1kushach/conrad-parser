from loguru import logger
from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from app.browser import click_if_present, login, navigate
from app.config import CATEGORY_URL
from app.scraper import scrape_balluff_products_links


def optional_text(page, css, timeout=3000):
    try:
        return " ".join(page.locator(css).first.inner_text(timeout=timeout).split())
    except PlaywrightTimeoutError:
        return None


def handle_initial_load(page: Page, email: str, password: str):
    navigate(page, f"{CATEGORY_URL}?page=1")
    # Handle initial popups.
    click_if_present(page, "Annehmen")
    click_if_present(page, "Ich bin Privatkunde")
    click_if_present(page, "Konto")
    click_if_present(
        page,
        css="a[data-unique-tracking='loginButton']",
        timeout=10000,
        sleep_after=5,
    )
    # Login.
    login(page, email, password)


def get_total_pages(page: Page) -> str:
    logger.info("Getting total pages")
    # Get last page number.
    pagination = page.locator("ul.pagination__list")
    last_second_span = pagination.locator("li").nth(-2).locator("span")
    total_pages = last_second_span.inner_html()
    return total_pages


def get_all_links(page: Page, total_pages: int, max_links) -> list[str]:
    all_links = []
    for n in range(1, int(total_pages)):
        print(f"Total links - {len(all_links)}")
        if max_links is not None and len(all_links) >= max_links:
            unique_links = list(dict.fromkeys(all_links))
            if len(unique_links) >= max_links:
                break

        links = scrape_balluff_products_links(page, n, 100)
        all_links.extend(links)
    all_links = list(dict.fromkeys(all_links))
    if max_links is not None:
        all_links = all_links[:max_links]
    return all_links
