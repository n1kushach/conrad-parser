from app.config import BASE_URL
from playwright.sync_api import Page, Error as PlaywrightTimeoutError
from urllib.parse import urljoin
from app.product.get_datasheet import get_datasheet


def get_breadcrumbs(page: Page) -> dict:
    crumbs = page.locator(".ce-breadcrumb > .ce-breadcrumb-element")
    crumbs.first.wait_for(state="attached", timeout=15000)

    items = crumbs.evaluate_all(
        """els => els.map(el => ({
            text: el.textContent.trim(),
            href: el.getAttribute('href'),
        }))"""
    )

    return {
        "breadcrumbs": [
            {
                "name": i["text"],
                "url": urljoin(BASE_URL, i["href"]) if i["href"] else None,
            }
            for i in items
        ]
    }


def get_product_details(page: Page):
    product_main_image = page.locator("#productMainImage").get_attribute("src")
    product_title = page.locator("#ProductTitle").inner_text().strip()
    technical_detail_rows = page.locator(
        ".productImageAndData__dataTechnical div.justify-between:has(> div.font-bold)"
    )

    try:
        technical_detail_rows.first.wait_for(state="attached", timeout=15000)
    except PlaywrightTimeoutError:
        return {}  # product without a spec table

    pairs = technical_detail_rows.evaluate_all(
        """rows => rows.map(row => {
            const name = row.querySelector(':scope > div.font-bold');
            const value = row.querySelector(':scope > div:not(.font-bold)');
            return [name?.textContent.trim(), value?.textContent.trim()];
        })"""
    )
    technical_details = {name: " ".join(value.split())
                         for name, value in pairs if name and value}
    # pdf_info = get_datasheet(page)
    stock_text = page.locator(
        "#currentOfferAvailability [data-prerenderer='availabilityText']").first.inner_text().strip()
    stock = {"Stock": stock_text}
