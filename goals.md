Build Goals (for your agent)

When you're done, the human should be able to do this:

Setup phase (5 min)


 Clone repo
 Copy .env.example to .env
 Fill in 3 API keys (Databento, generate WEBHOOK_SECRET, optional Telegram)
 Save .env


Build phase (1-2 hours, agent does this)


 Download 5 years of MES 1-minute bars from Databento → data/MES_1m.parquet
 Build backtest harness (backtest_orb.py) that loads data and runs ORB logic
 Build lie-detector (lie_detector.py) that audits for same-bar fills + look-ahead bias
 Build strategy templates (ORB working, KLBS/IB50/TOM/MGC stubbed)
 Build bridge components (BarBridge.cs, OrderRouter.cs, live_runner.py, dashboard.py)
 Scaffold Railway backend (webhook_receiver.py) but don't deploy yet
 Generate Supabase schema and setup guide (but don't deploy yet)
 Stub ASM dashboard (basic version)
 Stub Telegram integration (basic version)
 Create README.md files in each folder explaining what was built


First test (backtest — local, no NinjaTrader needed)

Human runs:

python backtest_orb.py

Success looks like:

Total trades: ~1,000
Win rate: ~25%
Profit factor: < 1 (unprofitable, expected)
Max drawdown: ~$2,500
Sharpe: < 1
Expectancy: negative

Then:

python lie_detector.py

Success looks like:

Same-bar fill audit: PASS (no same-bar fills)
Look-ahead bias audit: PASS (no future data leaks)

Second test (live bridge — local, with NinjaTrader demo)

Human installs NinjaTrader, gets demo credentials, opens a chart. Then:

python live_runner.py

And in NT8:


BarBridge indicator runs on chart
OrderRouter strategy runs on chart
Dummy curl command posts a test signal
Order appears in NT8's Orders tab
Fill comes back within 1-2 seconds


Success looks like:


live_runner.log shows "Signal fired: LONG"
BarBridge.log shows CSV written
OrderRouter.log shows "Signal received, order placed"
Dashboard shows the signal and fill in the UI


Third test (paper trading — 3-5 sessions)

Human runs live_runner + dashboard for a few live trading sessions (demo data, simulated fills).

Success looks like:


Signals fire when expected (matches what backtest would do on same bars)
Fills come back within 1-2 seconds
Dashboard captures every trade
Logs are clean, no errors
System doesn't crash for a full 6+ hour session


End state (after tests pass)

Human has:


A working backtest harness (confidence in numbers)
A working local bridge (signals → orders → fills, all logged)
Paper-trading proof (live system works as expected)
4 strategy framework docs (KLBS, IB50, TOM, MGC — read /docs)
ASM dashboard (ready to deploy, just need Supabase)
Railway backend scaffolded (ready to deploy)
Supabase schema + guide (ready to deploy)
Telegram setup guide (ready to wire)


Human's next move:


Pick one framework
Backtest it (use the harness)
Walk-forward validate it (use lie-detector + research guide)
When edge is real, deploy to Railway + Supabase
Run live on a prop account eval


What the agent must NOT do


Don't make the ORB profitable. It's unprofitable on purpose (scaffolding).
Don't hardcode API keys. Always use .env.
Don't assume user has Supabase/Railway yet. Scaffold, don't deploy.
Don't skip the lie-detector. Same-bar fills and look-ahead bias are silent killers.
Don't over-engineer. Keep it simple. One strategy logic file, one backtest file, one bridge.


Code quality checklist


 All Python code uses .env for secrets (not hardcoded)
 All logs go to files + stdout (trackable)
 No blocking I/O in NT8 scripts (UI stays responsive)
 All strategy logic is testable in isolation (backtest can run it)
 All OHLCV data is parquet (not CSV — faster, smaller)
 All timestamps are timezone-aware (ET assumed unless specified)
 All fills use NEXT bar's open (never same bar)
 Commission + slippage baked into backtest
 Bridge handles disconnects gracefully (logs, doesn't crash)
 Dashboard refreshes every 5 seconds (light, not CPU-heavy)


Success criteria

When the human runs this:

bashgit clone <repo>
cd repo
cp .env.example .env
# Edit .env with 3 API keys
python backtest_orb.py  # Runs, shows stats
python lie_detector.py  # Passes audits

And later:

bashpython live_runner.py   # Starts, tails CSV, waits for bars
# NT8 with BarBridge + OrderRouter running
# ... signals fire, fills come back, dashboard updates

Then the agent has succeeded.
