"""
Scheduler for running price scrapes on a schedule.

Usage:
    python -m execution.scheduler --once     # Run once and exit
    python -m execution.scheduler --daemon   # Run continuously
"""

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import (
    SCRAPE_INTERVAL_HOURS,
    PRICE_CHANGE_THRESHOLD_PERCENT,
    load_competitors_config
)
from execution.scraper import PriceScraper
from execution.storage import init_database, save_price, detect_price_change
from execution.telegram import TelegramBot


def run_scrape_cycle() -> dict:
    """
    Execute a full scrape cycle: scrape -> detect changes -> alert -> save.

    Returns:
        Summary dictionary with counts and changes
    """
    print(f"\n{'='*60}")
    print(f"Starting scrape cycle at {datetime.now().isoformat()}")
    print('='*60)

    # Initialize
    init_database()
    scraper = PriceScraper()
    bot = TelegramBot()
    config = load_competitors_config()

    threshold = config.get("alerts", {}).get(
        "price_change_threshold",
        PRICE_CHANGE_THRESHOLD_PERCENT
    )
    batch_alerts = config.get("alerts", {}).get("batch_alerts", True)

    # Scrape all competitors
    results = scraper.scrape_all()

    # Process results
    changes = []
    success_count = 0
    error_count = 0

    for result in results:
        if not result["success"]:
            error_count += 1
            continue

        success_count += 1

        # Check for price change
        change = detect_price_change(
            product_id=result["product_id"],
            competitor_name=result["competitor"],
            new_price=result["price"],
            threshold_percent=threshold
        )

        if change:
            changes.append(change)

        # Save to database (always, regardless of change)
        save_price(
            competitor_name=result["competitor"],
            product_id=result["product_id"],
            price=result["price"],
            product_name=result.get("name"),
            stock_status=result.get("stock_status"),
            url=result["url"]
        )

    # Send alerts
    alerts_sent = 0
    if changes:
        try:
            if batch_alerts:
                bot.send_batch_alerts(changes)
                alerts_sent = 1
            else:
                for change in changes:
                    bot.send_price_alert(change)
                    alerts_sent += 1
            print(f"\nSent {alerts_sent} alert(s) for {len(changes)} price change(s)")
        except Exception as e:
            print(f"\nFailed to send alerts: {e}")

    # Summary
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_products": len(results),
        "successful_scrapes": success_count,
        "errors": error_count,
        "price_changes": len(changes),
        "alerts_sent": alerts_sent
    }

    print(f"\n{'-'*60}")
    print(f"Cycle complete:")
    print(f"  Scraped: {success_count}/{len(results)} products")
    print(f"  Changes detected: {len(changes)}")
    print(f"  Alerts sent: {alerts_sent}")
    print('-'*60)

    return summary


def run_daemon(interval_hours: float = None):
    """
    Run scraper continuously at specified interval.

    Args:
        interval_hours: Hours between scrape cycles (default from settings)
    """
    interval = interval_hours or SCRAPE_INTERVAL_HOURS
    interval_seconds = interval * 3600

    print(f"Starting daemon mode (interval: {interval} hours)")
    print("Press Ctrl+C to stop\n")

    try:
        while True:
            run_scrape_cycle()

            next_run = datetime.now().timestamp() + interval_seconds
            next_run_str = datetime.fromtimestamp(next_run).strftime("%Y-%m-%d %H:%M:%S")
            print(f"\nNext run at: {next_run_str}")

            time.sleep(interval_seconds)

    except KeyboardInterrupt:
        print("\n\nDaemon stopped by user")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Price monitor scheduler")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--daemon", action="store_true", help="Run continuously")
    parser.add_argument(
        "--interval",
        type=float,
        help=f"Hours between runs (default: {SCRAPE_INTERVAL_HOURS})"
    )

    args = parser.parse_args()

    if args.once:
        summary = run_scrape_cycle()
        return 0 if summary["errors"] == 0 else 1

    if args.daemon:
        run_daemon(args.interval)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
