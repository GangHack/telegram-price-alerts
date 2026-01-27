# Directive: Troubleshooting

> Common issues and their solutions.

## Scraping Issues

### TimeoutError: Waiting for selector

**Symptoms:**
```
TimeoutError: Timeout 30000ms exceeded waiting for selector ".price"
```

**Causes:**
1. Selector is wrong
2. Page loads slowly
3. Element is inside iframe
4. JavaScript hasn't rendered yet

**Solutions:**
1. Test selector manually in browser DevTools
2. Increase timeout: `TIMEOUT_MS=60000` in `.env`
3. Check if content is in iframe (requires different approach)
4. Use more specific wait: `wait_for_selector` with different state

### 403 Forbidden / Access Denied

**Symptoms:**
- Page returns 403 status
- "Access Denied" or CAPTCHA page

**Causes:**
- Bot detection triggered
- IP blocked
- User agent blocked

**Solutions:**
1. Increase delays between requests
2. Check `USER_AGENT` in `.env` is realistic
3. Try running with `--visible` flag to debug
4. Enable proxy rotation: `PROXY_URL=...` in `.env`
5. Reduce scrape frequency

### Empty Price (None returned)

**Symptoms:**
- Scrape succeeds but price is None
- Raw text shows non-numeric content

**Causes:**
1. Wrong selector
2. Price format not recognized
3. Content loaded after initial parse

**Solutions:**
1. Verify selector in DevTools
2. Check `price_raw` in output for actual text
3. Update `parse_price()` if format is unusual

## Telegram Issues

### 400 Bad Request

**Symptoms:**
```
HTTP 400: Bad Request
```

**Causes:**
1. Invalid bot token
2. Invalid chat ID
3. Malformed message

**Solutions:**
1. Verify token with BotFather
2. Re-fetch chat ID from getUpdates
3. Test with simple message: `--test "Hello"`

### 401 Unauthorized

**Symptoms:**
```
HTTP 401: Unauthorized
```

**Cause:** Bot token is invalid or revoked.

**Solution:** Get new token from @BotFather.

### Message Not Received

**Causes:**
1. Never started chat with bot
2. Bot blocked by user
3. Wrong chat ID

**Solutions:**
1. Send any message to your bot first
2. Unblock bot in Telegram
3. Re-fetch chat ID

## Database Issues

### Database Locked

**Symptoms:**
```
sqlite3.OperationalError: database is locked
```

**Cause:** Multiple processes accessing database.

**Solution:** Only run one scheduler instance at a time.

### No Price History

**Symptoms:**
- `--history` returns empty
- No changes detected

**Cause:** Database not initialized or wrong product ID.

**Solutions:**
1. Run: `python -m execution.storage --init`
2. Check product ID matches config exactly

## Environment Issues

### Module Not Found

**Symptoms:**
```
ModuleNotFoundError: No module named 'playwright'
```

**Solutions:**
```bash
pip install -r requirements.txt
playwright install chromium
```

### Browser Launch Failed

**Symptoms:**
```
Error: Browser closed unexpectedly
```

**Solutions:**
1. Install browser: `playwright install chromium`
2. On Linux, install deps: `playwright install-deps`
3. Try `--visible` mode to see what's happening

## Quick Diagnostics

```bash
# Test single URL scrape
python -m execution.scraper --test --url "https://example.com" --selector ".price" --visible

# Test Telegram
python -m execution.telegram --test "Diagnostic message"

# Check database
python -m execution.storage --init
python -m execution.storage --history --product "test-product"

# Full test run
python -m execution.scheduler --once
```

## Learnings

- Add specific issues and solutions here as you encounter them
