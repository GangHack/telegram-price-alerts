# Directive: Add New Competitor

> How to add a new competitor website to the price monitor.

## Goal

Add a new competitor's product pages to the monitoring system so their prices are tracked alongside existing competitors.

## Inputs

- **Competitor name**: Human-readable name (e.g., "TechStore")
- **Base URL**: Root domain (e.g., "https://techstore.com")
- **Product URLs**: List of product pages to monitor
- **CSS selectors**: Selectors for price, name, and stock elements

## Process

### 1. Inspect the Target Page

Open the product page in Chrome and use DevTools (F12):

1. Right-click the price element → "Inspect"
2. Find a unique selector:
   - ID: `#price` (best)
   - Class: `.product-price` (good)
   - Data attribute: `[data-testid="price"]` (good)
   - Complex: `.product-info .price-now` (fallback)

3. Test in Console:
   ```javascript
   document.querySelector('.your-selector').textContent
   ```

### 2. Add to Configuration

Edit `config/competitors.yaml`:

```yaml
competitors:
  # ... existing competitors ...

  - name: "NewCompetitor"
    base_url: "https://newcompetitor.com"
    enabled: true
    products:
      - id: "product-slug"  # Unique identifier
        url: "/products/product-page"  # Path after base_url
        selectors:
          price: ".price-selector"
          name: "h1.product-title"  # Optional
          stock: ".stock-status"    # Optional
```

### 3. Test the Scrape

```bash
python -m execution.scraper --test --url "https://newcompetitor.com/products/page" --selector ".price-selector"
```

If successful, you'll see the extracted price. If not, adjust the selector.

### 4. Run Full Test

```bash
python -m execution.scheduler --once
```

Verify the new competitor appears in the output.

## Outputs

- Updated `config/competitors.yaml`
- New competitor products tracked in `data/prices.db`

## Edge Cases

- **Dynamic prices (JavaScript)**: Playwright handles this, but may need `wait_for_selector`
- **Multiple price formats**: The `parse_price()` function handles $, €, commas, etc.
- **Anti-bot protection**: Add longer delays or enable proxy in `.env`
- **Price in iframe**: Requires special handling (update scraper.py)

## Learnings

- [Template] Document site-specific quirks here as you discover them
