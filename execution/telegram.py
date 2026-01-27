"""
Telegram notification sender.

Usage:
    python -m execution.telegram --test "Hello from price monitor!"
"""

import argparse
import sys
from pathlib import Path

import httpx

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


class TelegramBot:
    """Simple Telegram bot for sending notifications."""

    BASE_URL = "https://api.telegram.org/bot{token}"

    def __init__(self, token: str = None, chat_id: str = None):
        self.token = token or TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or TELEGRAM_CHAT_ID
        self.api_url = self.BASE_URL.format(token=self.token)

    def _validate_config(self):
        """Check if bot is configured."""
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN not configured")
        if not self.chat_id:
            raise ValueError("TELEGRAM_CHAT_ID not configured")

    def send_message(self, text: str, parse_mode: str = "Markdown") -> dict:
        """
        Send a text message to the configured chat.

        Args:
            text: Message text (supports Markdown)
            parse_mode: "Markdown" or "HTML"

        Returns:
            Telegram API response
        """
        self._validate_config()

        response = httpx.post(
            f"{self.api_url}/sendMessage",
            json={
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": parse_mode
            },
            timeout=30
        )

        response.raise_for_status()
        return response.json()

    def format_price_alert(self, change: dict) -> str:
        """
        Format a price change into a Telegram message.

        Args:
            change: Dictionary from storage.detect_price_change()

        Returns:
            Formatted message string
        """
        if change["type"] == "new_product":
            return (
                f"*New Product Detected*\n\n"
                f"Product: `{change['product_id']}`\n"
                f"Competitor: {change['competitor']}\n"
                f"Price: ${change['new_price']:.2f}"
            )

        direction = "increased" if change["direction"] == "up" else "decreased"
        emoji = "📈" if change["direction"] == "up" else "📉"

        return (
            f"{emoji} *Price Alert*\n\n"
            f"Product: `{change['product_id']}`\n"
            f"Competitor: {change['competitor']}\n\n"
            f"Old price: ${change['old_price']:.2f}\n"
            f"New price: ${change['new_price']:.2f}\n"
            f"Change: {change['change_percent']:+.1f}% ({direction})"
        )

    def send_price_alert(self, change: dict) -> dict:
        """
        Send a formatted price alert.

        Args:
            change: Dictionary from storage.detect_price_change()

        Returns:
            Telegram API response
        """
        message = self.format_price_alert(change)
        return self.send_message(message)

    def send_batch_alerts(self, changes: list[dict]) -> dict:
        """
        Send multiple price changes in a single message.

        Args:
            changes: List of change dictionaries

        Returns:
            Telegram API response
        """
        if not changes:
            return {"ok": True, "result": "No changes to report"}

        lines = ["*Price Monitor Update*\n"]

        for change in changes:
            if change["type"] == "new_product":
                lines.append(
                    f"• NEW: `{change['product_id']}` @ ${change['new_price']:.2f}"
                )
            else:
                emoji = "📈" if change["direction"] == "up" else "📉"
                lines.append(
                    f"{emoji} `{change['product_id']}`: "
                    f"${change['old_price']:.2f} → ${change['new_price']:.2f} "
                    f"({change['change_percent']:+.1f}%)"
                )

        message = "\n".join(lines)
        return self.send_message(message)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Telegram notification sender")
    parser.add_argument("--test", metavar="MESSAGE", help="Send a test message")

    args = parser.parse_args()

    if args.test:
        try:
            bot = TelegramBot()
            result = bot.send_message(args.test)
            if result.get("ok"):
                print("Message sent successfully!")
            else:
                print(f"Failed: {result}")
            return 0
        except ValueError as e:
            print(f"Configuration error: {e}", file=sys.stderr)
            return 1
        except httpx.HTTPError as e:
            print(f"HTTP error: {e}", file=sys.stderr)
            return 1

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
