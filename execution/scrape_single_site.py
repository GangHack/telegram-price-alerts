"""
Scrape a single website and extract structured data.

Usage:
    python execution/scrape_single_site.py <url> [--selectors selector1,selector2]

Output:
    .tmp/scraped_data.json
"""

import argparse
import sys
from datetime import datetime

import httpx
from bs4 import BeautifulSoup

from utils import save_json


def scrape_url(url: str, selectors: list[str] | None = None) -> dict:
    """
    Fetch and parse a URL, extracting text content.

    Args:
        url: Target URL to scrape
        selectors: Optional CSS selectors to extract specific elements

    Returns:
        Dictionary with extracted data
    """
    response = httpx.get(url, timeout=30, follow_redirects=True)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove script and style elements
    for element in soup(["script", "style", "nav", "footer"]):
        element.decompose()

    result = {
        "url": url,
        "timestamp": datetime.now().isoformat(),
        "status_code": response.status_code,
        "title": soup.title.string if soup.title else None,
    }

    if selectors:
        # Extract specific elements
        result["selections"] = {}
        for selector in selectors:
            elements = soup.select(selector)
            result["selections"][selector] = [el.get_text(strip=True) for el in elements]
    else:
        # Extract all text content
        result["text"] = soup.get_text(separator="\n", strip=True)

    return result


def main():
    parser = argparse.ArgumentParser(description="Scrape a single website")
    parser.add_argument("url", help="URL to scrape")
    parser.add_argument("--selectors", help="Comma-separated CSS selectors", default=None)

    args = parser.parse_args()

    selectors = args.selectors.split(",") if args.selectors else None

    try:
        data = scrape_url(args.url, selectors)
        output_path = save_json(data, "scraped_data.json")
        print(f"Success: Data saved to {output_path}")
        return 0
    except httpx.HTTPError as e:
        print(f"HTTP Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
