"""
SQLite storage for price history.

Usage:
    python -m execution.storage --history --product "product-id"
"""

import argparse
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import DATABASE_PATH


def get_connection() -> sqlite3.Connection:
    """Get database connection with row factory."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize database schema."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            competitor_name TEXT NOT NULL,
            product_id TEXT NOT NULL,
            product_name TEXT,
            price REAL NOT NULL,
            currency TEXT DEFAULT 'USD',
            stock_status TEXT,
            url TEXT,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_product_id ON prices(product_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_scraped_at ON prices(scraped_at)
    """)

    conn.commit()
    conn.close()


def save_price(
    competitor_name: str,
    product_id: str,
    price: float,
    product_name: str = None,
    currency: str = "USD",
    stock_status: str = None,
    url: str = None
) -> int:
    """
    Save a price record to the database.

    Returns:
        The ID of the inserted record.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO prices (competitor_name, product_id, product_name, price, currency, stock_status, url)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (competitor_name, product_id, product_name, price, currency, stock_status, url))

    record_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return record_id


def get_latest_price(product_id: str, competitor_name: str = None) -> Optional[dict]:
    """
    Get the most recent price for a product.

    Args:
        product_id: The product identifier
        competitor_name: Optional competitor filter

    Returns:
        Dictionary with price data or None if not found.
    """
    conn = get_connection()
    cursor = conn.cursor()

    if competitor_name:
        cursor.execute("""
            SELECT * FROM prices
            WHERE product_id = ? AND competitor_name = ?
            ORDER BY scraped_at DESC
            LIMIT 1
        """, (product_id, competitor_name))
    else:
        cursor.execute("""
            SELECT * FROM prices
            WHERE product_id = ?
            ORDER BY scraped_at DESC
            LIMIT 1
        """, (product_id,))

    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


def get_price_history(product_id: str, limit: int = 100) -> list[dict]:
    """
    Get price history for a product.

    Args:
        product_id: The product identifier
        limit: Maximum number of records to return

    Returns:
        List of price records, newest first.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM prices
        WHERE product_id = ?
        ORDER BY scraped_at DESC
        LIMIT ?
    """, (product_id, limit))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def detect_price_change(
    product_id: str,
    competitor_name: str,
    new_price: float,
    threshold_percent: float = 0
) -> Optional[dict]:
    """
    Check if price has changed from the last recorded value.

    Args:
        product_id: The product identifier
        competitor_name: The competitor name
        new_price: The newly scraped price
        threshold_percent: Minimum % change to trigger (0 = any change)

    Returns:
        Dictionary with change details if threshold exceeded, else None.
    """
    last = get_latest_price(product_id, competitor_name)

    if not last:
        # New product, no previous price
        return {
            "type": "new_product",
            "product_id": product_id,
            "competitor": competitor_name,
            "new_price": new_price,
            "old_price": None,
            "change_percent": None
        }

    old_price = last["price"]

    if old_price == new_price:
        return None  # No change

    change_percent = ((new_price - old_price) / old_price) * 100

    if abs(change_percent) >= threshold_percent:
        return {
            "type": "price_change",
            "product_id": product_id,
            "competitor": competitor_name,
            "old_price": old_price,
            "new_price": new_price,
            "change_percent": round(change_percent, 2),
            "direction": "up" if change_percent > 0 else "down"
        }

    return None


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Price storage operations")
    parser.add_argument("--init", action="store_true", help="Initialize database")
    parser.add_argument("--history", action="store_true", help="Show price history")
    parser.add_argument("--product", help="Product ID for history lookup")
    parser.add_argument("--limit", type=int, default=20, help="Limit history results")

    args = parser.parse_args()

    if args.init:
        init_database()
        print(f"Database initialized at: {DATABASE_PATH}")
        return 0

    if args.history:
        if not args.product:
            print("Error: --product required with --history", file=sys.stderr)
            return 1

        history = get_price_history(args.product, args.limit)
        if not history:
            print(f"No history found for product: {args.product}")
            return 0

        print(f"\nPrice history for: {args.product}")
        print("-" * 60)
        for record in history:
            print(f"  {record['scraped_at']} | {record['competitor_name']} | ${record['price']:.2f}")

        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
