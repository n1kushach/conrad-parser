import os

from dotenv import load_dotenv
from playwright.sync_api import (
    sync_playwright,
)
from seleniumbase import sb_cdp

from app.browser import click_if_present, login, navigate
from app.config import CATEGORY_URL
from app.scraper import scrape_product

load_dotenv()


def save_links(links):
    # Remove duplicates while preserving order.
    unique_links = list(dict.fromkeys(links))

    with open("balluff_links.txt", "w", encoding="utf-8") as file:
        file.write("\n".join(unique_links))

    print("\n========== RESULTS ==========")

    for link in unique_links:
        print(link)

    print(f"\nTotal unique products: {len(unique_links)}")
    print("Saved to balluff_links.txt")


def main():
    email = os.environ["CONRAD_EMAIL"]
    password = os.environ["CONRAD_PASSWORD"]

    sb = sb_cdp.Chrome()

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(sb.get_endpoint_url())

        context = browser.contexts[0]

        page = context.pages[0] if context.pages else context.new_page()

        # Open category page.
        navigate(page, f"{CATEGORY_URL}?page=1")
        # navigate(
        #     page, "https://www.conrad.de/de/p/balluff-induktiver-sensor-bes0068-1-st-3416652.html")

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

        print(
            scrape_product(
                page,
                "https://www.conrad.de/de/p/balluff-abstandssensor-induktiv-baw-m18mg-uac16f-s04g-k-baw0029-m18-x-1-nicht-buendig-analog-spannung-o-x-h-18-mm-x-65-3416817.html",
            )
        )

        # # Get last page number.
        # pagination = page.locator("ul.pagination__list")
        # last_second_span = pagination.locator("li").nth(-2).locator("span")

        # total_pages = last_second_span.inner_html()
        # print(total_pages)

        # # Scrape products.
        # all_links = []
        # for n in range(1, int(total_pages)):
        #     print(f"Total links - {len(all_links)}")
        #     if MAX_LINKS is not None and len(all_links) >= MAX_LINKS:
        #         unique_links = list(dict.fromkeys(all_links))
        #         if len(unique_links) >= MAX_LINKS:
        #             break

        #     links = scrape_balluff_products_links(page, n, 100)
        #     all_links.extend(links)


if __name__ == "__main__":
    main()
