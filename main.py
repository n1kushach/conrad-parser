import os

from dotenv import load_dotenv
from playwright.sync_api import (
    sync_playwright,
)
from seleniumbase import sb_cdp

from app.config import MAX_LINKS
from app.product.parsers import save_products
from app.scraper import scrape_product
from app.util import get_all_links, get_total_pages, handle_initial_load

load_dotenv()


def main():
    email = os.environ["CONRAD_EMAIL"]
    password = os.environ["CONRAD_PASSWORD"]

    sb = sb_cdp.Chrome()

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(sb.get_endpoint_url())
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()

        handle_initial_load(page, email, password)
        total_pages = get_total_pages(page)
        all_links = get_all_links(page, int(total_pages), MAX_LINKS)

        all_products = []
        for index, link in enumerate(all_links, start=1):
            try:
                print(f"\nProduct {index}/{len(all_links)}")

                row = scrape_product(page, link)
                all_products.append(row)

            except Exception as e:
                print(f"Error scraping {link}: {e}")

        # Save all rows.
        save_products(all_products)


if __name__ == "__main__":
    main()
