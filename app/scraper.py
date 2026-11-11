from urllib.parse import urljoin

from loguru import logger
from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from app.browser import navigate
from app.config import BASE_URL, CATEGORY_URL
from app.product.details import get_product_details


def scrape_balluff_products_links(page: Page, page_number: int, max_links: int | None = None):
    """Return BALLUFF product links from one page, stopping at max_links."""
    if max_links is not None and max_links <= 0:
        return []

    url = f"{CATEGORY_URL}?page={page_number}"
    logger.info(f"\nScraping page {page_number}: {url}")

    navigate(page, url)

    titles = page.locator("h2[data-purpose='product-title']")

    try:
        titles.first.wait_for(state="visible", timeout=15000)
    except PlaywrightTimeoutError:
        logger.error(f"No product titles found on page {page_number}")
        return []

    balluff = titles.filter(has=page.locator("span.font-bold", has_text="BALLUFF"))

    links = []

    for item in balluff.all():
        href = item.locator("a").get_attribute("href")
        if href:
            product_url = urljoin(BASE_URL, href)
            links.append(product_url)
            logger.info(f"BALLUFF: {product_url}")

    logger.info(f"Found {len(links)} BALLUFF products on page {page_number}")
    return links


def scrape_product(page: Page, link: str) -> dict:
    navigate(page, link)
    return get_product_details(page)
