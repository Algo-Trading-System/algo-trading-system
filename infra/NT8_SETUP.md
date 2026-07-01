# NT8 Setup — Execution Platform Landscape

Your trading system runs through NinjaTrader 8. This explains what to connect, what to watch for, and how to keep it alive.

## Connection types

NT8 supports multiple data feeds and order routing. For this system, use:

**Preferred (what we use):**
- **Data feed:** Rithmic (via Rithmic bridge in NT8)
- **Order routing:** Rithmic (for prop firms) or IB (for personal account)
- **Account:** Sim101 (demo), or your prop firm account

**Why Rithmic?** Low latency (critical for intraday), reliable, used by most prop traders.

**Alternatives:**
- Tradovate (good, lower latency than IB)
- NT Brokerage (built-in, but slower)
- Interactive Brokers (IBKR, good for personal accounts, higher latency)

## Chart setup

1. **Open NT8, create new chart**
2. **Instrument:** MES 09-26 (Micro S&P 500, front month)
3. **Data feed:** Rithmic (or your chosen feed)
4. **Account:** Sim101 (demo) or your funded account
5. **Chart properties:**
   - Bar type: Minute
   - Bar size: 1 minute
   - Timezone: America/Chicago (UTC-6)

## Add the bridge

1. **BarBridge indicator:**
   - Tools → Edit NinjaScript → Indicator
   - Create new, paste BarBridge.cs
   - Compile (F5)
   - Add → Indicator → BarBridge (on your chart)

2. **OrderRouter strategy:**
   - Tools → Edit NinjaScript → Strategy
   - Create new, paste OrderRouter.cs
   - Compile (F5)
   - Strategies → Add Strategy → OrderRouter (on your chart)

Both must run on the SAME chart.

## Survival rules (critical)

These prevent crashes, disconnects, and mystery issues:

### 1. Windows updates
- **Never** let Windows auto-update while NT8 is running
- Update on weekends or after market closes
- Set: Settings → Update & Security → Active hours (9:30 AM - 4:00 PM ET)

### 2. Sleep mode
- **Never** let your machine sleep
- Settings → Power & sleep → Sleep: Never
- Also: Never put NT8 in background for >10 min

### 3. Network
- **Hardwired Ethernet** (not WiFi) if possible
- If VPS: High-speed connection to your VPS provider

### 4. NT8 restart automation
If on VPS, add a daily restart (best practice):

**Windows Task Scheduler:**
1. Task Scheduler → Create Basic Task
2. Name: "Restart NinjaTrader 8"
3. Trigger: Daily, 4:00 PM ET (after market close)
4. Action: Restart computer
5. This kills NT8, restarts cleanly

### 5. Logging
BarBridge and OrderRouter log to:
- `data/live/MES_1m.csv` (bar data)
- `NT8-Logs/BarBridge.log` (bar writes)
- `NT8-Logs/OrderRouter.log` (signal receives + order placements)

**Check these logs if anything goes wrong.**

### 6. Bracket submission pattern
For stop/target orders, NT8 supports "bracket" orders (entry + stop + target in one go):

```csharp
EnterLong(qty, "Entry");
// Then set stops/targets via ExitLongStop() and ExitLongProfit()
```

**Better:** Use one entry order, manage stops/targets separately in strategy code. Cleaner, more predictable.

### 7. Position reconciliation
NT8 tracks position state. Every bar, verify:
- NT8's position matches your strategy state
- No "stuck" orders (orders placed but not filled)
- No disconnects that created phantom positions

If position is wrong, manually flatten in NT8, restart strategy.

## Maintenance windows

**Never run live signals during:**
- Market opens/closes (9:30 AM / 4:00 PM ET) — high slippage, connectivity issues
- FOMC announcements — extreme volatility, orders may reject
- Economic data releases — same reason

**When to run:**
- 10:00 AM - 3:55 PM ET (middle of day, quiet)
- Outside earnings season if possible

## Common issues + fixes

**"No connection to data feed"**
→ Restart NT8. If persists, restart Windows.

**"Bracket order rejected"**
→ Use manual stop/target instead of bracket orders. Simpler.

**"Order fills at weird prices"**
→ Check: 1) Commission assumptions in backtest, 2) Slippage model, 3) Bid-ask spread during bar

**"BarBridge stopped writing bars"**
→ Check logs. Likely: NT8 crashed, or data feed disconnected. Restart both.

**"OrderRouter not receiving signals"**
→ Check: 1) live_runner is running, 2) OrderRouter HTTP listener is active, 3) Firewall isn't blocking localhost:8765

## Backup plan

If NT8 crashes mid-day:
1. Restart NT8 immediately
2. Check positions in your prop firm dashboard (not NT8 — they're the source of truth)
3. Reconcile: flatten positions in NT8 if needed
4. Verify live_runner and OrderRouter are still running
5. Resume trading

**Never panic-close positions.** They're already in the prop firm's system.