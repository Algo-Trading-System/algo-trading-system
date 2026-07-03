# Risk Controls — Account-Level Circuit Breakers

These are the 6 account-level rules that protect you from catastrophic loss. Strategy-specific stops come from your research — these are the account guardrails.

## Layer 1: Daily Loss Limit (Circuit Breaker #1)

Once you've lost X dollars in a single calendar day, you're done trading for that day.

**Typical:** $500 - $1,000 per account per day (adjust per account size).

**How to enforce:**
- Track daily P&L in live_runner (reset at midnight ET)
- Before each entry, check: `if daily_loss + (worst_case_trade_loss) > daily_limit: don't enter`
- At midnight, reset daily_loss = 0

Example:
```python
daily_loss = -250  # Down $250 today
new_trade_risk = 500  # Worst case on next trade (from your strategy research)
if daily_loss + new_trade_risk > 500:  # Would exceed daily limit
    skip_entry()  # Don't trade
```

## Layer 2: Account Drawdown Limit (Circuit Breaker #2)

If your account is down more than X% from its peak (peak-to-trough), stop all trading.

**Typical:** 5-10% max drawdown (depends on account size and strategy edge confidence).

**How to enforce:**
- Track running equity in Supabase (or logs for now)
- Compute: `current_dd_pct = (peak_equity - current_equity) / peak_equity * 100`
- If `current_dd_pct > max_dd_pct`: flatten all positions, don't enter new ones
- Wait for equity to recover above 95% of peak before resuming

Example:
```python
peak_equity = 50000
current_equity = 47500
current_dd_pct = (50000 - 47500) / 50000 * 100 = 5%

if current_dd_pct > 5:  # Hit limit
    flatten_all()
    stop_trading()
```

## Layer 3: Position Size per Trade

Not every account can afford to lose $500 on a single bad trade.

**Calculate max contracts per trade:**

```
Max Contracts = (Daily Loss Limit / 2) / (Worst Case Loss Per Contract)
```

Example: Daily limit $500, worst case per contract is $62.50
```
Max = (500 / 2) / 62.50 = 4 contracts max per trade
```

Hard rule: never submit an order larger than this.

## Layer 4: Maximum Contracts Per Trade (Prop Firm Limit)

Some accounts have their own rules. Prop firms often say "max 10 contracts per trade" or "max $5,000 notional exposure."

**Check your prop firm agreement.** Encode it:

```python
MAX_CONTRACTS_PER_TRADE = 10  # Your prop firm's rule

if contracts > MAX_CONTRACTS_PER_TRADE:
    contracts = MAX_CONTRACTS_PER_TRADE
```

## Layer 5: Correlation Hedge (Multi-Strategy)

If you're running KLBS + IB50 + TOM on the same account, they can all be LONG simultaneously (correlated losses).

**Option 1:** Run them on separate accounts (cleanest).

**Option 2:** Add a correlation gate — if one strategy is already LONG 5 contracts, the next strategy's LONG signal scales down or doesn't fire.

```python
if existing_position_contracts > 0 and signal_direction == existing_position_direction:
    # Reduce size or skip
    contracts = max(1, contracts - existing_position_contracts)
```

## Layer 6: Intraday Equity Snapshots

Every N minutes, log: `current_equity, current_dd_pct, daily_loss, open_positions`.

If something glitches (NT8 crashes, broker network hiccup), you have a record of when it happened and what state you were in.

---

## Summary: The Gates in Order

1. **Per-trade position size** — calculate max contracts before entry
2. **Daily loss limit** — stop if you've lost enough today
3. **Account DD limit** — stop if you're down too much from peak
4. **Prop firm limits** — respect their max contracts/notional rules
5. **Correlation hedge** — don't go all-in if multiple strategies agree
6. **Snapshots** — log state every N minutes for debugging

All 6 must pass before an order enters NT8.

---

## Prop Firm Rules

Every prop firm has slightly different rules. **Read your account agreement.** Common ones:

- **Max daily loss**: Varies ($500-$2k)
- **Max drawdown**: Varies (5-10%)
- **Max contracts per trade**: Often 10-50
- **Max notional exposure**: Often $100k-$500k
- **Holding time**: Some have max hours (e.g., no overnight holds)

Code these as constants at the top of live_runner:

```python
PROP_FIRM_RULES = {
    'Tradeify': {'max_dd_pct': 5, 'max_daily_loss': 500, 'max_contracts': 20},
    'Lucid': {'max_dd_pct': 10, 'max_daily_loss': 1000, 'max_contracts': 50},
}
```

Then check against the account you're trading on before each entry.

---

## Manual Override Kill Switch

In `live_runner.py`, add a file-based kill switch:

```python
# Check if 'STOP_TRADING' file exists
if os.path.exists('STOP_TRADING'):
    print("STOP_TRADING file detected. Halting all signals.")
    exit()
```

If something goes truly wrong, create a file named `STOP_TRADING` in your repo root. live_runner detects it on the next bar and exits cleanly.
