"""
Playwright-based web scraper for competitor prices.

Usage:
    python -m execution.scraper --test --url "https://example.com/product"
    python -m execution.scraper --all
"""

import argparse
import random
import re
import sys
import time
from pathlib import Path
from typing import Optional

from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeout

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import (
    HEADLESS,
    TIMEOUT_MS,
    USER_AGENT,
    PROXY_URL,
    load_competitors_config
)
from execution.logger import get_logger

logger = get_logger()


def random_delay(min_sec: float = 2, max_sec: float = 5):
    """Human-like random delay between requests."""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)


def parse_price(text: str) -> Optional[float]:
    """
    Extract numeric price from text.

    Handles formats like: $99.99, €89,99, 99.99 USD, etc.
    """
    if not text:
        return None

    # Remove currency symbols and whitespace
    cleaned = re.sub(r'[^\d.,]', '', text.strip())

    # Handle European format (1.234,56) vs US format (1,234.56)
    if ',' in cleaned and '.' in cleaned:
        if cleaned.rindex(',') > cleaned.rindex('.'):
            # European: 1.234,56
            cleaned = cleaned.replace('.', '').replace(',', '.')
        else:
            # US: 1,234.56
            cleaned = cleaned.replace(',', '')
    elif ',' in cleaned:
        # Could be European decimal or US thousands
        parts = cleaned.split(',')
        if len(parts) == 2 and len(parts[1]) == 2:
            # Likely European: 99,99
            cleaned = cleaned.replace(',', '.')
        else:
            # Likely US thousands: 1,234
            cleaned = cleaned.replace(',', '')

    try:
        return float(cleaned)
    except ValueError:
        return None


class PriceScraper:
    """Scraper for extracting prices from competitor websites."""

    def __init__(self, headless: bool = None, timeout_ms: int = None):
        self.headless = headless if headless is not None else HEADLESS
        self.timeout_ms = timeout_ms or TIMEOUT_MS
        self.user_agent = USER_AGENT
        self.proxy_url = PROXY_URL

    def _get_browser_args(self) -> dict:
        """Get browser launch arguments."""
        args = {
            "headless": self.headless,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ]
        }

        if self.proxy_url:
            args["proxy"] = {"server": self.proxy_url}

        return args

    def _setup_page(self, page: Page):
        """Configure page for stealth scraping."""
        # Set viewport to common desktop size
        page.set_viewport_size({"width": 1920, "height": 1080})

        # Override webdriver detection
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

    def scrape_product(
        self,
        url: str,
        selectors: dict,
        competitor_name: str = "Unknown"
    ) -> dict:
        """
        Scrape a single product page.

        Args:
            url: Full URL to the product page
            selectors: Dict with keys: price, name (optional), stock (optional)
            competitor_name: Name of the competitor for logging

        Returns:
            Dictionary with scraped data
        """
        result = {
            "url": url,
            "competitor": competitor_name,
            "success": False,
            "price": None,
            "name": None,
            "stock_status": None,
            "error": None
        }

        with sync_playwright() as p:
            browser = p.chromium.launch(**self._get_browser_args())
            context = browser.new_context(user_agent=self.user_agent)
            page = context.new_page()

            self._setup_page(page)

            try:
                # Navigate to page
                page.goto(url, timeout=self.timeout_ms, wait_until="domcontentloaded")

                # Wait for price element
                price_selector = selectors.get("price")
                if price_selector:
                    page.wait_for_selector(price_selector, timeout=self.timeout_ms)
                    price_element = page.query_selector(price_selector)
                    if price_element:
                        price_text = price_element.text_content()
                        result["price"] = parse_price(price_text)
                        result["price_raw"] = price_text

                # Get product name (optional)
                name_selector = selectors.get("name")
                if name_selector:
                    name_element = page.query_selector(name_selector)
                    if name_element:
                        result["name"] = name_element.text_content().strip()

                # Get stock status (optional)
                stock_selector = selectors.get("stock")
                if stock_selector:
                    stock_element = page.query_selector(stock_selector)
                    if stock_element:
                        result["stock_status"] = stock_element.text_content().strip()

                result["success"] = result["price"] is not None

            except PlaywrightTimeout:
                result["error"] = "Timeout waiting for elements"
            except Exception as e:
                result["error"] = str(e)
            finally:
                browser.close()

        return result

    def scrape_competitor(self, competitor_config: dict) -> list[dict]:
        """
        Scrape all products for a single competitor.

        Args:
            competitor_config: Competitor configuration from YAML

        Returns:
            List of scrape results
        """
        results = []
        name = competitor_config["name"]
        base_url = competitor_config["base_url"]
        products = competitor_config.get("products", [])

        logger.info(f"Scraping {name}...")

        for product in products:
            product_url = base_url + product["url"]
            selectors = product.get("selectors", {})

            result = self.scrape_product(
                url=product_url,
                selectors=selectors,
                competitor_name=name
            )
            result["product_id"] = product["id"]
            results.append(result)

            if result["success"]:
                logger.info(f"{product['id']}: ${result['price']:.2f}")
            else:
                logger.error(f"{product['id']}: {result['error']}")

            # Random delay between products
            random_delay()

        return results

    def scrape_all(self) -> list[dict]:
        """
        Scrape all configured competitors.

        Returns:
            List of all scrape results
        """
        config = load_competitors_config()
        competitors = config.get("competitors", [])
        scrape_config = config.get("scraping", {})

        all_results = []

        for competitor in competitors:
            if not competitor.get("enabled", True):
                logger.debug(f"Skipping disabled competitor: {competitor['name']}")
                continue

            results = self.scrape_competitor(competitor)
            all_results.extend(results)

            # Delay between competitors
            delay_min = scrape_config.get("delay_min_seconds", 2)
            delay_max = scrape_config.get("delay_max_seconds", 5)
            random_delay(delay_min, delay_max)

        return all_results


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Price scraper")
    parser.add_argument("--test", action="store_true", help="Test mode (single URL)")
    parser.add_argument("--url", help="URL to scrape in test mode")
    parser.add_argument("--selector", default=".price", help="Price selector for test mode")
    parser.add_argument("--all", action="store_true", help="Scrape all configured competitors")
    parser.add_argument("--visible", action="store_true", help="Run browser in visible mode")

    args = parser.parse_args()

    scraper = PriceScraper(headless=not args.visible)

    if args.test:
        if not args.url:
            logger.error("Error: --url required with --test")
            return 1

        result = scraper.scrape_product(
            url=args.url,
            selectors={"price": args.selector},
            competitor_name="Test"
        )

        logger.info(f"Result:")
        logger.info(f"  URL: {result['url']}")
        logger.info(f"  Success: {result['success']}")
        logger.info(f"  Price: {result['price']}")
        logger.info(f"  Raw: {result.get('price_raw', 'N/A')}")
        if result['error']:
            logger.error(f"  Error: {result['error']}")

        return 0 if result['success'] else 1

    if args.all:
        results = scraper.scrape_all()

        success_count = sum(1 for r in results if r["success"])
        logger.info(f"Summary: {success_count}/{len(results)} successful")

        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
