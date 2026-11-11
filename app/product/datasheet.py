from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

DATASHEET_BUTTON = "#pdp-datasheet-main-btn"


def get_datasheet(page: Page, timeout: int = 10_000) -> dict:
    """Return {"label": ..., "url": ...} for the product datasheet.

    The datasheet is a <button> with no href, so we click it and capture
    the PDF URL from whatever the click triggers: a download, a popup/new
    tab, or a network response with a PDF content type.
    """
    button = page.locator(DATASHEET_BUTTON)

    try:
        button.first.wait_for(state="attached", timeout=3000)
    except PlaywrightTimeoutError:
        return {"label": None, "url": None}  # product without a datasheet

    try:
        label = (
            page.locator("span.font-semibold", has_text="Datenblatt")
            .first.inner_text(timeout=2000)
            .strip()
        )
    except PlaywrightTimeoutError:
        label = None

    found: list[str] = []
    popups = []

    def on_response(resp):
        if "pdf" in resp.headers.get("content-type", "").lower():
            found.append(resp.url)

    def on_download(download):
        found.append(download.url)

    def on_popup(popup):
        popups.append(popup)

    page.on("response", on_response)
    page.on("download", on_download)
    page.on("popup", on_popup)

    try:
        button.first.click(timeout=5000)

        waited = 0
        while not found and waited < timeout:
            page.wait_for_timeout(250)
            waited += 250
            for popup in popups:
                if popup.url and popup.url != "about:blank":
                    found.append(popup.url)
                    break
    finally:
        page.remove_listener("response", on_response)
        page.remove_listener("download", on_download)
        page.remove_listener("popup", on_popup)
        for popup in popups:
            try:
                popup.close()
            except Exception:
                pass

    return {"label": label, "url": found[0] if found else None}
