System Architecture

Your trading system has 7 components. Understand how they connect, and you understand the whole machine.

The 7 components

[Historical Data] ──→ [Backtest] ──→ [Metrics]
                                        │
                                        ▼
                                   [Strategy Logic]
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
                    ▼                   ▼                   ▼
            [NinjaTrader 8]       [Railway Backend]    [Supabase DB]
              (chart, orders)      (message broker)     (trade logs)
                    │                   │                   │
                    └───────────────────┼───────────────────┘
                                        │
                                        ▼
                                 [Monitoring Dashboard]
                                   (what you see)

1. Historical Data (Databento)


Job: 1-minute OHLCV bars for backtesting
Input: Databento API key
Output: data/MES_1m.parquet (5 years of bars)
Who runs it: You (once), then your backtest reads it
Cost: Free on signup credits


2. Backtest Harness (Python)


Job: Run strategy logic on historical bars, measure P&L
Input: data/MES_1m.parquet + strategy logic
Output: output/orb_trades.csv + stats (win rate, profit factor, max DD, Sharpe)
Who runs it: You (during research)
Why: Proves the strategy has edge before risking capital


3. Strategy Logic (Python)


Job: Given N bars of history, decide: go LONG, go SHORT, or stay FLAT
Input: DataFrame of OHLCV + current position state
Output: Signal {action, confidence}
Who runs it: Backtest harness (research) + live_runner (live trading)
Key rule: Same code runs both backtest AND live. If backtest says 65% win rate, live should match.


4. NinjaTrader 8 (Windows)


Job: Display charts, manage accounts, execute orders
Two scripts run inside it:

BarBridge (indicator): Writes bars to CSV or POSTs to Railway
OrderRouter (strategy): Receives signals, places orders via NT8 API



Who runs it: You (chart stays open while system trades)
Data flow: Chart → bars → Bridge → Python strategy → signals → OrderRouter → NT8 API → orders


5. Railway Backend (FastAPI, production-only)


Job: Message broker between NT8 and Python
Replaces: CSV file in development mode
Input: Bars from BarBridge, signals from live_runner
Output: Orders routed back to OrderRouter, fills logged to Supabase
Who runs it: Deployed once, runs 24/7
When: After paper-trading passes, before live deployment
Why: Keeps your system running while laptop sleeps


6. Supabase Database (Postgres)


Job: Persistent storage for bars, signals, fills, trades
Tables:

bars — every 1-min bar (instrument, time, OHLCV)
signals — every signal fired (strategy, timestamp, action, confidence)
fills — every order execution (price, size, slippage, P&L)
trades — closed trades (entry, exit, duration, R-multiple)
accounts — per-account snapshots (equity, drawdown, daily loss)



Who queries it: Monitoring dashboard, ASM, alerts
When: Optional for local paper-trading, essential for production


7. Monitoring Dashboard (Flask/React)


Job: Show you what's happening without watching charts
Displays:

Equity curve (real-time)
Drawdown % vs. daily limit
Win rate + R-multiple distribution
Recent trades + current positions
Connection status lights



Reads from: Logs (local) or Supabase (production)
When: Deploy immediately, update as you build


Two operating modes

Mode 1: Local Development (CSV-based)

[NT8 on laptop]
    │
    ├─ BarBridge → data/live/MES_1m.csv
    │
    └─ OrderRouter ← localhost:8765
         ↑
         │
    [live_runner.py] → polls CSV → runs strategy → POSTs signal
         │
         ├─ logs/runner.log
         ├─ NT8-Logs/OrderRouter.log
         │
    [dashboard.py] → reads logs → shows state

Pros:


No internet needed
Super simple to debug
Instant feedback


Cons:


Dies if laptop sleeps
Only works on one machine


Use for: Backtest validation + paper-trading + development

Mode 2: Production (Railway + Supabase)

[NT8 on VPS]
    │
    ├─ BarBridge ──HTTP POST──→ [Railway backend]
    │                                │
    └─ OrderRouter ←HTTP GET────────┘
         │                           │
         ├─ logs (stdout)    Supabase fill logging
         │                           │
         │                    [asm_dashboard] ← queries Supabase
         │                           │
         └───────────────────────────┼─→ [Telegram alerts]

Pros:


Runs 24/7 while you sleep
Scales to multiple strategies + accounts
Persistent data in Supabase
Real monitoring + alerts


Cons:


More moving parts
Costs money (Railway ~$5-10/mo, Supabase free tier)


Use for: Live paper-trading + eval + live money

Data flow (one complete cycle)


Bar closes in market (e.g., 10:01 ET on MES)
BarBridge (NT8 indicator) writes row to CSV or POSTs to Railway
live_runner (Python) reads new bar, runs strategy logic
Strategy compares bar history to rules, decides: LONG / SHORT / FLAT
live_runner POSTs signal to OrderRouter if action ≠ FLAT
OrderRouter (NT8 strategy) receives signal, calls EnterLong() or EnterShort()
NT8 places market order on Sim101 or real account
Broker fills order at market price
OrderRouter logs fill (timestamp, price, size, slippage)
Dashboard updates to show new position


Total latency (local): ~100-500ms from bar close to order placed
Total latency (Railway): ~1-2 seconds

Build order

Phase 1 (backtest + local bridge):


Data pipeline (download.py)
Backtest harness (backtest_orb.py + lie_detector.py)
Strategy logic (orb.py)
BarBridge.cs + OrderRouter.cs (NinjaScript)
live_runner.py + dashboard.py (Python)


Phase 2 (paper-trading validation):


Run live_runner + OrderRouter on demo for 3-5 sessions
Verify: signals match backtest expectations, fills are realistic, system is stable


Phase 3 (production, optional):


Create Supabase project
Create Railway project
Update BarBridge + OrderRouter to use Railway
Deploy live_runner to Railway
Deploy dashboard to Railway
Wire Telegram alerts


Phase 4 (real money):


Connect NT8 to prop firm
Adjust account routing + position sizing
Run on eval account
Once eval passes, run on live funded account


Key principles

Same code, two modes: Strategy logic runs identically in backtest and live. If backtest lies, live will too. Honest backtesting is non-negotiable.

Explicit data flow: Every bar, signal, and fill is logged. You can trace exactly what happened at any timestamp.

Separation of concerns: Backtest doesn't know about NT8. NT8 doesn't know about strategy research. Each layer is independent.

Scalable from day 1: The architecture works for 1 strategy on 1 account. Same architecture scales to 10 strategies on 5 accounts with zero code changes.

Sanity checks (before you run anything)


 Data pipeline works (download.py fetches bars)
 Backtest runs without errors (backtest_orb.py)
 Lie-detector passes (no same-bar fills, no look-ahead bias)
 Strategy logic is testable in isolation (orb.py returns consistent signals on same bar history)
 BarBridge writes CSV rows at bar close (check timestamp)
 OrderRouter listens on localhost:8765 (curl test passes)
 live_runner reads CSV without errors (tail runner.log while market is open)
 Dashboard refreshes and shows trades (open localhost:5000)
 Paper-trading results match backtest expectations (±1-2 ticks for slippage)


All green? You have a working system. Now research the edge.
