# Competitor Price Monitor

Automated price monitoring system that scrapes competitor websites and sends real-time Telegram alerts when prices change.

## Problem Solved

E-commerce businesses need to track competitor prices but manual checking is slow and unreliable. This tool automates the process, enabling faster reaction to market changes (hours to minutes).

## Key Features

- **Playwright Web Scraping** - Handles JavaScript-heavy e-commerce sites
- **Anti-Detection** - Stealth mode, random delays, realistic user agents
- **Real-Time Alerts** - Telegram notifications when prices change
- **Price History** - SQLite database for trend analysis
- **YAML Configuration** - Easy to add/remove competitors without code changes

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3.12 | Core language |
| Playwright | Browser automation |
| SQLite | Price history storage |
| Telegram Bot API | Real-time notifications |
| YAML | Configuration management |

## Architecture

![System Architecture](architecture-diagram.png)

The system runs on a scheduled timer and follows this workflow:
1. **Scrape** - Visit competitor URLs and extract prices using Playwright
2. **Compare** - Check new prices against database history
3. **Alert** - Send Telegram notification if price changed
4. **Store** - Save new price record to SQLite for trend analysis

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Add your Telegram credentials to `.env`:
- `TELEGRAM_BOT_TOKEN` - Get from @BotFather
- `TELEGRAM_CHAT_ID` - Get from /getUpdates API

### 3. Configure Competitors

Edit `config/competitors.yaml`:

```yaml
competitors:
  - name: "CompetitorStore"
    base_url: "https://store.example.com"
    products:
      - id: "product-123"
        url: "/products/item-page"
        selectors:
          price: ".product-price"
          name: "h1.title"
```

### 4. Run

```bash
# Single scrape
python -m execution.scheduler --once

# Continuous monitoring
python -m execution.scheduler --daemon
```

## Project Structure

```
price-monitor/
├── config/
│   ├── competitors.yaml    # Sites and products to monitor
│   └── settings.py         # Configuration loader
├── data/
│   └── prices.db           # SQLite price history
├── directives/             # Documentation/SOPs
│   ├── add_competitor.md
│   ├── alert_rules.md
│   ├── scrape_workflow.md
│   └── troubleshooting.md
├── execution/              # Core scripts
│   ├── scraper.py          # Playwright scraper
│   ├── storage.py          # Database operations
│   ├── telegram.py         # Notifications
│   ├── scheduler.py        # Orchestration
│   └── utils.py            # Helpers
├── tests/
├── .env.example
├── requirements.txt
└── README.md
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `python -m execution.scheduler --once` | Run single scrape cycle |
| `python -m execution.scheduler --daemon` | Run continuously |
| `python -m execution.scheduler --daemon --interval 2` | Custom interval (hours) |
| `python -m execution.scraper --test --url URL --selector SEL` | Test single URL |
| `python -m execution.telegram --test "message"` | Test Telegram connection |
| `python -m execution.storage --history --product ID` | View price history |

## Adding a New Competitor

1. Inspect the product page (F12 in Chrome)
2. Find the price element's CSS selector
3. Test: `document.querySelector('.selector').textContent`
4. Add to `config/competitors.yaml`
5. Test: `python -m execution.scraper --test --url "..." --selector "..."`

## License

MIT
