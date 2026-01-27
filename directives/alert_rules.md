# Directive: Alert Rules

> Configuration and logic for when to send price alerts.

## Goal

Define when and how to notify users about price changes, balancing signal quality with timeliness.

## Alert Triggers

### 1. Price Change

Triggered when a product's price differs from the last recorded value.

**Configuration:**
```yaml
# config/competitors.yaml
alerts:
  price_change_threshold: 0  # Percentage threshold
```

| Threshold | Behavior |
|-----------|----------|
| `0` | Alert on ANY price change |
| `5` | Alert only if change > 5% |
| `10` | Alert only if change > 10% |

**Example:**
- Old price: $100
- New price: $95
- Change: -5%
- With threshold 0: ALERT
- With threshold 10: No alert

### 2. New Product Detected

Triggered when a product appears in scrape results but has no price history.

```yaml
alerts:
  notify_on_new_product: true
```

### 3. Stock Change (Optional)

Triggered when stock status changes (e.g., "In Stock" → "Out of Stock").

```yaml
alerts:
  notify_on_stock_change: true
```

## Alert Formatting

### Single Alert
```
📉 Price Alert

Product: `iphone-15-pro`
Competitor: TechStore

Old price: $999.99
New price: $899.99
Change: -10.0% (decreased)
```

### Batch Alert
```
Price Monitor Update

• NEW: `galaxy-s24` @ $799.99
📉 `iphone-15-pro`: $999.99 → $899.99 (-10.0%)
📈 `pixel-8`: $599.99 → $649.99 (+8.3%)
```

## Telegram Configuration

### Get Bot Token
1. Message @BotFather on Telegram
2. Send `/newbot`
3. Follow prompts, get token

### Get Chat ID
1. Message your bot
2. Visit: `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. Find `"chat":{"id": YOUR_ID}`

### Test Connection
```bash
python -m execution.telegram --test "Hello from price monitor!"
```

## Rate Limits

Telegram allows 30 messages/second to the same chat. With batching enabled, this is never an issue.

## Learnings

- Start with threshold 0 to see all changes, then increase if too noisy
- Batch alerts are recommended (one message vs. many)
- Stock alerts are useful for high-demand products
