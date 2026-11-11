from urllib.parse import urljoin

from loguru import logger
from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from app.config import BASE_URL
from app.product.datasheet import get_datasheet
from app.product.documents import get_documents  # adjust to where you put it
from app.product.parsers.parsers import (
    get_breadcrumbs,
    get_identifiers,
    get_prices,
    get_product_description,
    get_product_highlights,
    get_seller,
    get_stock,
    get_technical_data,
)


def _safe(fn, page: Page, default):
    """Run an optional parser. A timeout gives `default` instead of crashing the product."""
    try:
        return fn(page)
    except PlaywrightTimeoutError:
        logger.warning("{} timed out on {}", getattr(fn, "__name__", "parser"), page.url)
        return default


def get_product_details(page: Page, url: str | None = None) -> dict:
    # Required: waits for the page and fails loudly if it never loads
    product_title = page.locator("#ProductTitle").inner_text(timeout=15000).strip()

    # Optional: None instead of a 30 second wait if missing
    try:
        src = page.locator("#productMainImage").first.get_attribute("src", timeout=3000)
    except PlaywrightTimeoutError:
        src = None

    identifiers = get_identifiers(page)
    stock = get_stock(page)
    seller = get_seller(page) or {}
    specs = get_technical_data(page)

    prices = _safe(get_prices, page, {}) or {}
    breadcrumbs = _safe(get_breadcrumbs, page, {}).get("breadcrumbs") or []
    highlights = _safe(get_product_highlights, page, {}) or {}
    description = _safe(get_product_description, page, {}).get("description") or {}

    pdf_info = _safe(get_datasheet, page, {}) or {}
    documents = _safe(lambda p: get_documents(p, key="type"), page, {}).get("documents") or {}

    # get_seller returns {"<German label>": name, "href": url}
    seller_name = next((v for k, v in seller.items() if k != "href"), None)

    return {
        "url": url or page.url,
        "title": product_title,
        "main_image": urljoin(BASE_URL, src) if src else None,
        **identifiers,  # EAN, Hst.-Teile-Nr., Bestell-Nr.
        **stock,  # Stock
        **prices,  # total_price, main_price
        "seller": seller_name,
        "seller_url": seller.get("href"),
        "breadcrumbs": " > ".join(c["name"] or "" for c in breadcrumbs),
        "breadcrumb_urls": " | ".join(c["url"] or "" for c in breadcrumbs),
        "highlights": " | ".join(highlights.get("description_list", [])) or None,
        **{f"description_{k}": v for k, v in description.items() if k},
        "datasheet_label": pdf_info.get("label"),
        "datasheet_url": pdf_info.get("url"),
        **{f"doc_{k}": v for k, v in documents.items()},
        **{f"spec_{k}": v for k, v in specs.items()},
    }
