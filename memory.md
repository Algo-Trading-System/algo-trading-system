System Architecture & Memory (for your agent)

You're building a mechanical trading system. Read this so you understand how all the pieces fit.

The big picture

[Historical data] ──> [Backtest] ──> [Edge metrics]
                                          │
                                          ▼
                                    [Live strategy]
                                          │
                    ┌─────────────────────┼─────────────────────┐
                    │                     │                     │
                    ▼                     ▼                     ▼
              [NT8 chart]           [Railway backend]      [Supabase logs]
                  │                        │                     │
                  │                        │                     ▼
                  └──> [Orders] ───────────┼────────> [Monitoring UI]
                                          │
                                          ▼
                                    [Telegram alerts]

The parts

1. Backtest (local)


Files: backtest_orb.py, download_data.py, lie_detector.py
Job: Load historical 1-minute bars from Databento, run a strategy logic, measure P&L, win rate, profit factor, max drawdown
Input: .env (DATABENTO_API_KEY), data/MES_1m.parquet
Output: output/orb_trades.csv, console stats
Truth: The numbers here tell you if an idea has edge or is garbage. Lie detection is critical.


2. Strategy logic (local Python)


Files: strategies/orb.py, strategies/klbs_template.py, etc.
Job: Given a bar of data (OHLCV + rolling history), decide: go LONG, go SHORT, or FLAT
Logic: Rule-based or ML-filtered (KLBS uses GradientBoostingClassifier over ~30 features)
Used by: Backtest harness AND live_runner
Principle: Same code runs both backtest and live. If backtest says 65% win rate, live should match (roughly).


3. Bridge: Local mode (development)


BarBridge.cs (NinjaScript Indicator): Runs on your NT8 chart. Every bar close, writes data/live/MES_1m.csv
live_runner.py (Python): Polls the CSV every 1s. Runs strategy logic. If signal fires, POSTs to localhost:8765/signal
OrderRouter.cs (NinjaScript Strategy): Runs on same chart. HTTP listener on port 8765. Receives POST, places order via NT8's EnterLong() / EnterShort() / ExitLong() etc.
Dashboard.py (Flask): Reads logs, shows current state, signal history, errors. Runs on localhost:5000
Transport: CSV file on disk (simple, zero networking, sub-1s latency)
Use case: Development + paper trading. You're verifying the rails work before touching real money.


4. Bridge: Production mode (always-on)


Same three pieces, different transport:

BarBridge stops writing CSV; POSTs bars to https://<railway-url>/nt8/bar (HMAC-signed)
live_runner stops polling CSV; subscribes to bar bus on Railway backend
OrderRouter POSTs fills back to Railway on execution



Railway.app (FastAPI backend):

Receives bars from NT8 BarBridge
In-memory bar bus (strategies subscribe)
Dispatches signals back to OrderRouter (HMAC verification)
Logs everything to stdout (Railway captures it)
Pushes fills to Supabase



Why Railway? Runs 24/7 while your laptop sleeps. Low latency to NT8 VPS. One place to manage secrets + env vars.


5. Data storage (Supabase)


What's stored:

Every bar (instrument, time, OHLCV)
Every signal (strategy, timestamp, action, confidence)
Every fill (order ID, price, size, time, slippage, account)
Trade summaries (entry, exit, P&L, R-multiple, MFE/MAE)
Account snapshots (drawdown, daily loss, payout eligibility)



Why Supabase? Hosted Postgres. Free tier covers small accounts. SQL-native (easy to query). Auth built-in.
Schema: Defined in infra/supabase_schema.sql. Agent loads this and creates tables.


6. Monitoring (ASM)


What it shows:

Real-time equity curve per strategy per account
Current drawdown vs. limit (live headroom)
Daily loss tracking (did you hit the max daily loss rule yet?)
Win rate, R-multiple distribution, trade calendar
Position reconciliation (is the live position matching strategy state?)
Manual overrides (flatten an account manually if needed)
Kill switches (pause a strategy, stop a feed, etc.)



Reads from: Supabase (queries live data)
Runs on: Your laptop or Railway (we suggest Railway for 24/7 uptime)


7. Alerts (Telegram)


What triggers:

New fill (entry or exit)
No-fill (signal fired, but no order came back — network issue?)
Drawdown approaching limit
Max daily loss hit
Strategy error (exception, bad signal format, etc.)
Stale feed (no bars for 5+ minutes — data connection down?)



Why Telegram? Phone-native. Instant. You don't stare at a screen; your phone tells you.


Environment variables (.env)

DATABENTO_API_KEY=<your-key>           # For historical data download
WEBHOOK_SECRET=<random-32-bytes>       # Shared HMAC secret between NT8 and Railway
RAILWAY_TOKEN=<your-railway-token>     # Optional, if agent deploys for you
SUPABASE_URL=<your-supabase-url>       # After Supabase setup
SUPABASE_KEY=<your-supabase-anon-key>  # After Supabase setup
TELEGRAM_BOT_TOKEN=<your-bot-token>    # Optional, for alerts
TELEGRAM_CHAT_ID=<your-chat-id>        # Optional, where to send alerts

Agent reads .env and uses these to:


Fetch data from Databento
Sign requests to Railway
Write to Supabase
Send Telegram messages


Workflow: local development


Backtest: Run python backtest_orb.py. Verify numbers + lie detection.
Paper-trade: Start live_runner. Chart opens. Bars flow. BarBridge writes CSV. live_runner reads it. Signals fire. OrderRouter places orders. Dashboard shows it. Logs capture it. All on local.
Test 5-10 sessions. Does the live signal match what backtest would have done? Are fills realistic?
Move to production: Lift the bridge to Railway. Same code, different transport (HTTP instead of CSV).


Workflow: production (Railway + Supabase)


Deploy Railway backend: Agent walks you through it. FastAPI app receives bars, dispatches signals, logs fills.
Update BarBridge/OrderRouter: Point to Railway URL instead of localhost. HMAC-sign requests.
Wire Supabase: Railway pushes fills to Supabase. ASM reads from Supabase. Queries are live.
Wire Telegram: Railway POSTs alerts to Telegram. You get notified on your phone.
Deploy ASM: Run on Railway or your laptop. Reads Supabase. Shows you everything.
Walk away: System runs 24/7. Strategies fire. Fills come back. Telegram tells you. Dashboard shows everything.


What the agent needs to build


Backtest harness — runs a strategy on historical data
Strategy templates — ORB, KLBS, IB50, TOM, MGC (you research params)
Bridge (local + production) — bars → strategy → orders → fills
Dashboard — simple web UI showing current state
Railway backend — FastAPI app for production transport
Supabase schema — tables for bars, signals, fills, trades, accounts
ASM — monitoring dashboard (reads Supabase, shows everything)
Telegram layer — sends alerts


Each folder has a README.md telling the agent how to build each piece.

Key principles


Same code runs backtest and live. If backtest says 65%, live should match (roughly).
The lie-detector catches obvious bugs. Same-bar fills, look-ahead bias. Agent runs it on every backtest.
Every decision is logged. Signal fired? Logged. Fill came back? Logged. Order rejected? Logged. No guessing.
Transport swaps, logic stays. Local CSV → Railway HTTP. Same strategy logic, different plumbing.
You own the edge. Agent builds the machine. You research the edge. Framework docs explain the logic.
Monitoring is non-negotiable. You don't watch charts. Your phone tells you if something breaks.


Strategy frameworks (provided, you research)


KLBS — Key-level mean reversion. Price stretches too far from a level, fade the move. ML filter on top.
IB50 — Initial balance retracement. Fade extreme move in first 60 min.
TOM — Turn-of-month. Intraday inefficiencies at month boundaries.
MGC ORB — Time-of-day breakout. Opening range breakout on Micro Gold.


Logic is in /docs. You research parameters on historical data. Walk-forward validate. Then deploy.

That's it

The agent builds the machine. You research the edge. The docs explain both