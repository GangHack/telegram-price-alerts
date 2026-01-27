# Directive: Scrape Workflow

> Main workflow for running price scrapes and processing results.

## Goal

Execute a complete price monitoring cycle: scrape all competitors, detect price changes, send alerts, and store data.

## Execution Scripts

| Script | Purpose |
|--------|---------|
| `execution/scheduler.py` | Orchestrates the full workflow |
| `execution/scraper.py` | Playwright-based web scraping |
| `execution/storage.py` | SQLite database operations |
| `execution/telegram.py` | Send Telegram notifications |

## Process

### Quick Start

```bash
# Run once (manual trigger)
python -m execution.scheduler --once

# Run continuously (daemon mode)
python -m execution.scheduler --daemon

# Custom interval (2 hours instead of default 4)
python -m execution.scheduler --daemon --interval 2
```

### Workflow Steps

1. **Load Configuration**
   - Read `config/competitors.yaml`
   - Get list of enabled competitors and products

2. **Scrape Each Product**
   - Launch headless Chromium browser
   - Navigate to product URL
   - Wait for price element to load
   - Extract price, name, stock status
   - Random delay between requests (2-5 sec)

3. **Detect Changes**
   - Compare new price to last stored price
   - Apply threshold filter (if configured)
   - Flag new products

4. **Send Alerts**
   - Format price change messages
   - Send via Telegram Bot API
   - Batch multiple changes if configured

5. **Store Data**
   - Save all prices to SQLite (even unchanged)
   - Maintains full price history for analytics

## Configuration

### Environment Variables (`.env`)

```bash
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
SCRAPE_INTERVAL_HOURS=4
PRICE_CHANGE_THRESHOLD_PERCENT=0
```

### Alert Thresholds (`config/competitors.yaml`)

```yaml
alerts:
  price_change_threshold: 0    # 0 = all changes, 5 = only >5%
  notify_on_new_product: true
  batch_alerts: true           # Combine into one message
```

## Outputs

- **Telegram alerts**: Sent when prices change
- **Database records**: `data/prices.db`
- **Console logs**: Summary of each scrape cycle

## Error Handling

| Error | Action |
|-------|--------|
| Timeout | Skip product, continue with others |
| Selector not found | Log warning, skip product |
| Telegram API error | Log error, data still saved |
| Network error | Retry up to 3 times |

## Monitoring

View price history:
```bash
python -m execution.storage --history --product "product-id"
```

## Learnings

- Always save data BEFORE sending alerts (data is preserved if Telegram fails)
- Random delays are essential to avoid detection
- Test selectors manually before adding to config
