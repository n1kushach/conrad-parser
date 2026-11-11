from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


def get_documents(page: Page, key: str = "title", debug: bool = False, attempts: int = 2) -> dict:
    """Return {"documents": {<title>: <download url>}} for every document
    in the "Dokumente & Downloads" section.

    key="title" -> "Datenblatt 3416652 BALLUFF Induktiver Sensor - BES0068, 1 St."
    key="type"  -> "Datenblatt" (same CSV column for every product)
    attempts    -> how many times to click a button if no URL was captured
    """
    context = page.context
    buttons = page.locator("[id^='pdp-datasheet-section-btn-']")
    try:
        buttons.first.wait_for(state="attached", timeout=3000)
    except PlaywrightTimeoutError:
        return {"documents": {}}  # product without downloads

    documents = {}

    for i in range(buttons.count()):
        button = buttons.nth(i)

        info = button.evaluate(
            """el => ({
                title: el.closest('div')?.querySelector('p')?.textContent.trim(),
                type: el.closest('article')?.querySelector('h2')?.textContent.trim(),
            })"""
        )

        name = (
            (info["type"] if key == "type" else info["title"])
            or button.get_attribute("id")
            or f"document_{i + 1}"
        )
        if name in documents:  # two documents with the same name
            name = f"{name} ({i + 1})"

        found, new_pages = [], []

        def on_response(resp):
            headers = resp.headers
            ctype = headers.get("content-type", "").lower()
            disposition = headers.get("content-disposition", "").lower()
            path = resp.url.split("?")[0].lower()

            if resp.url.startswith("http") and (
                "pdf" in ctype or "attachment" in disposition or path.endswith(".pdf")
            ):
                found.append(resp.url)

        def on_download(download):
            if debug:
                print(f"  [download] {download.url[:120]}")
            found.append(download.url)

        def on_new_page(new_page):
            if debug:
                print("  [new tab]")
            new_pages.append(new_page)
            new_page.on("download", on_download)

        context.on("response", on_response)
        context.on("page", on_new_page)
        page.on("download", on_download)

        try:
            for attempt in range(1, attempts + 1):
                before = page.url
                if debug:
                    print(f"Clicking {name[:60]!r} (attempt {attempt})")

                button.scroll_into_view_if_needed()
                button.click(timeout=5000)

                waited = 0
                while not found and waited < 6000:
                    page.wait_for_timeout(250)
                    waited += 250

                    for new_page in new_pages:  # tab that landed on a normal URL
                        if new_page.url.startswith("http") and new_page.url != page.url:
                            found.append(new_page.url)
                            break

                    if not found and page.url.startswith("http") and page.url != before:
                        found.append(page.url)  # opened in the same tab
                        page.go_back(wait_until="domcontentloaded")

                if found:
                    break
        except PlaywrightTimeoutError as e:
            if debug:
                print(f"  [click failed] {str(e).splitlines()[0]}")
        finally:
            context.remove_listener("response", on_response)
            context.remove_listener("page", on_new_page)
            page.remove_listener("download", on_download)
            for new_page in new_pages:
                try:
                    new_page.close()
                except Exception:
                    pass

        documents[name] = found[0] if found else None

    return {"documents": documents}
