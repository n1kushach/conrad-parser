import csv
from urllib.parse import urljoin

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from app.config import BASE_URL
from app.util import optional_text


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


def get_identifiers(page):
    items = page.locator("#eanCode, #manufacturerCode, #productCode")

    pairs = items.evaluate_all(
        """els => els.map(el => [
                el.querySelector(':scope > span:first-child')?.textContent.trim(),
                el.querySelector('button span.select-text')?.textContent.trim(),
            ])"""
    )

    return {label.rstrip(":").strip(): value for label, value in pairs if label and value}


def get_stock(page):
    stock_text = optional_text(
        page, "#currentOfferAvailability [data-prerenderer='availabilityText']"
    )
    message_status = optional_text(page, ".message-status")
    stock = {"Stock": stock_text or message_status}
    return stock


def get_technical_details(page):
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
    technical_details = {name: " ".join(value.split()) for name, value in pairs if name and value}
    return technical_details


def get_seller(page) -> dict | None:
    span = page.locator("#productSellerInfo span:has(> a)").first

    try:
        data = span.evaluate(
            """el => {
                const a = el.querySelector(':scope > a');
                const label = [...el.childNodes]
                    .filter(n => n.nodeType === Node.TEXT_NODE)
                    .map(n => n.textContent)
                    .join(' ');
                return {label, name: a.textContent, href: a.getAttribute('href')};
            }""",
            timeout=3000,
        )
    except PlaywrightTimeoutError:
        return None  # no seller block on this page

    label = " ".join(data["label"].split())
    return {label: " ".join(data["name"].split()), "href": f"{BASE_URL}{data['href']}"}


def get_prices(page: Page) -> dict:
    total_price = page.locator('[data-e2e="total-price-label"]').inner_text().strip()
    main_price = page.locator('[data-e2e="main-price"]').inner_text().strip()

    return {"total_price": total_price, "main_price": main_price}


import logging

from playwright.sync_api import Page

logger = logging.getLogger(__name__)


def get_product_highlights(page: Page) -> dict:
    try:
        title_locator = page.locator("#descriptionTitle__productHighlights > h2")

        title_locator.wait_for(state="visible", timeout=5000)
        description_title = title_locator.inner_text().strip()

        list_locator = page.locator(".productHighlights__block ul.--descriptionList li")

        list_locator.first.wait_for(state="attached", timeout=5000)

        description_list = [item.inner_text().strip() for item in list_locator.all()]

        result = {
            "description_title": description_title,
            "description_list": description_list,
        }

        logger.info("Product highlights extracted: %s", result)

        return result

    except PlaywrightTimeoutError:
        logger.exception("Timeout while extracting product highlights")
        return {}

    except Exception:
        logger.exception("Unexpected error while extracting product highlights")
        return {}


def get_technical_data(page: Page) -> dict[str, str]:
    rows = page.locator("#productTechData dl.productTechData__list")
    try:
        rows.first.wait_for(state="attached", timeout=5000)
    except PlaywrightTimeoutError:
        return {}  # product without a technical data section

    pairs = rows.evaluate_all(
        """rows => rows.map(row => [
            row.querySelector(':scope > dt')?.textContent.trim(),
            row.querySelector(':scope > dd .productTechData__definitionDescription')?.textContent.trim(),
        ])"""
    )

    return {
        " ".join(name.split()): " ".join(value.split()) for name, value in pairs if name and value
    }


def get_product_description(page: Page):
    product_description_title = page.locator("div #productDescription div h2").inner_text().strip()
    product_description = (
        page.locator(
            "div #productDescription #descriptionTitle__productDescription .productDescription .text-body"
        )
        .inner_text()
        .strip()
    )
    attributes_notes_title = optional_text(
        page,
        "#productDescriptionWrapper #attributesNotes_facts #descriptionTitle__attributesNotes_facts div h3",
    )
    DESCRIPTION_LI = (
        "#productDescriptionWrapper #attributesNotes_facts "
        "#descriptionTitle__attributesNotes_facts ul > li"
    )
    items = page.locator(DESCRIPTION_LI)
    try:
        items.first.wait_for(state="attached", timeout=3000)
    except PlaywrightTimeoutError:
        return {"Description": None}  # product without this list

    texts = items.evaluate_all("els => els.map(el => el.textContent.trim())")
    cleaned = [" ".join(t.split()) for t in texts if t.strip()]
    return {
        "description": {
            product_description_title: product_description,
            attributes_notes_title: " | ".join(cleaned) or None,
        }
    }


def flatten_product(product: dict) -> dict:
    flattened = {}

    for key, value in product.items():
        if isinstance(value, dict):
            flattened.update(value)
        else:
            flattened[key] = value

    return flattened


def save_products(products):
    if not products:
        print("No products found.")
        return

    # Flatten nested dictionaries.
    products = [flatten_product(product) for product in products]

    # Collect all unique columns.
    fieldnames = list(dict.fromkeys(key for product in products for key in product.keys()))

    with open(
        "balluff_products.csv",
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(products)

    print(f"Successfully saved {len(products)} products.")
