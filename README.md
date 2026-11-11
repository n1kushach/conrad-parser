# conrad.de Parser

A Python scraper for [conrad.de](https://www.conrad.de) that collects product data for 100 Balluff products (example product: [Balluff BES0068 inductive sensor](https://www.conrad.de/de/p/balluff-induktiver-sensor-bes0068-1-st-3416652.html)) and saves it to a CSV file.

The parser works under an authorized (logged-in) account.

## Tech stack

- Python 3.9+
- [Playwright](https://playwright.dev/python/) for browser automation
- [loguru](https://github.com/Delgan/loguru) for logging
- `csv` (standard library) for output

## Installation

```bash
git clone https://github.com/n1kushach/conrad-parser.git
cd conrad-parser
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

> `playwright install chromium` downloads the browser binary that Playwright controls. It is required once after installing the dependencies.

## Configuration

Create a `.env` file in the project root with the credentials of your conrad.de account (register one at https://www.conrad.de if you don't have it):

```dotenv
CONRAD_EMAIL=email@example.com
CONRAD_PASSWORD=Test1234!
```

Do not commit this file. Make sure `.env` is listed in `.gitignore`.

## Usage

```bash
python main.py
```

When the run finishes, the scraped data is written to a CSV file in the project directory.

## How it works

**Login.** The scraper launches a Playwright browser, opens conrad.de, and signs in with the email and password from the `.env` file. All further requests are made within that authenticated session, so the data matches what a logged-in user sees.

**Data collection.** The scraper gathers links to Balluff products, then opens each product page and extracts the required fields. Progress, warnings, and errors are logged with loguru. The collected records (100 products) are written to a CSV file with the `csv` module.

## Notes

- Conrad may change its page layout, which can break selectors.
- Use the scraper responsibly and respect the website's terms of use.
