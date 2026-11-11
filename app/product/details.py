from playwright.sync_api import Page

from app.product.parsers import get_technical_data


def get_product_details(page: Page, url: str | None = None) -> dict:
    # Required: waits for the page and fails loudly if it never loads
    product_title = page.locator("#ProductTitle").inner_text(timeout=15000).strip()

    # # Optional: None instead of a 30 second wait if missing
    # try:
    #     src = page.locator("#productMainImage").first.get_attribute("src", timeout=3000)
    # except PlaywrightTimeoutError:
    #     src = None
    # product_main_image = urljoin(BASE_URL, src) if src else None

    # technical_details = get_technical_details(page)
    # identifiers = get_identifiers(page)
    # seller = get_seller(page) or {}
    # stock = get_stock(page)

    # try:
    #     breadcrumbs = get_breadcrumbs(page)["breadcrumbs"]
    # except PlaywrightTimeoutError:
    #     breadcrumbs = []

    # # Last: the click can open a popup or start a download
    # pdf_info = get_datasheet(page) or {}

    # # get_seller returns {"<German label>": name, "href": url}
    # seller_name = next((v for k, v in seller.items() if k != "href"), None)
    print(get_technical_data(page))
    return get_technical_data(page)
    # return {
    #     "url": url or page.url,
    #     "title": product_title,
    #     "main_image": product_main_image,
    #     **identifiers,  # EAN, Hst.-Teile-Nr., Bestell-Nr.
    #     **stock,  # Stock
    #     "seller": seller_name,
    #     "seller_url": seller.get("href"),
    #     "breadcrumbs": " > ".join(c["name"] or "" for c in breadcrumbs),
    #     "breadcrumb_urls": " | ".join(c["url"] or "" for c in breadcrumbs),
    #     "datasheet_label": pdf_info.get("label"),
    #     "datasheet_url": pdf_info.get("url"),
    #     **{f"spec_{k}": v for k, v in technical_details.items()},
    # }
