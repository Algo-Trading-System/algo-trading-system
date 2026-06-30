Bridge Module (Python ↔ NinjaTrader)

Your agent builds the local bridge here. Four files:


BarBridge.cs — NinjaScript indicator that writes bars to CSV
OrderRouter.cs — NinjaScript strategy that receives signals and places orders
live_runner.py — Python process that reads bars, runs strategy, posts signals
dashboard.py — Flask web UI showing current state


This is the development version (CSV-based, local). Production version (Railway HTTP) comes later.

What your agent builds

Prompt for your agent:


Build the local bridge for live paper trading:

File: BarBridge.cs (NinjaScript Indicator)


On each realtime bar close, append a row to data/live/MES_1m.csv
Columns: time, open, high, low, close, volume
Create header row if file doesn't exist
Flush after each write (no buffering)
Don't block UI thread (async or background)
Log to NT8-Logs/BarBridge.log


File: OrderRouter.cs (NinjaScript Strategy)


Launch HTTP listener on http://localhost:8765 at startup
On POST /signal with JSON {action: "LONG"|"SHORT"|"FLAT", instrument: "MES 09-26", quantity: 1}:

Place market order using EnterLong() / EnterShort() / ExitLong() / ExitShort()



Reject signals where instrument doesn't match chart's instrument
Log every signal received + NT8 order placement to NT8-Logs/OrderRouter.log
Catch and log all exceptions, never crash on malformed signals


File: live_runner.py


Poll data/live/MES_1m.csv every 1 second
On new row, run strategy logic (import from strategies/orb.py)
When signal fires, POST to http://localhost:8765/signal with JSON
Log every bar + every signal to logs/runner.log
Handle disconnects gracefully (log + retry)


File: dashboard.py (Flask)


Read logs/runner.log + NT8-Logs/OrderRouter.log
Show: current bridge state (connected? last signal time? last fill time?), signal history (last 50), errors (last 20)
Refresh every 5 seconds
Run on http://localhost:5000




How to use

Setup in NinjaTrader:


Edit NinjaScript → Indicator → paste BarBridge.cs → compile (F5)
Edit NinjaScript → Strategy → paste OrderRouter.cs → compile (F5)
Open MES 09-26 chart on demo connection
Apply BarBridge indicator to chart (Add → Indicator → BarBridge)
Apply OrderRouter strategy to chart (Add → Strategy → OrderRouter)


Run locally:

bashpython live_runner.py      # In terminal 1
python dashboard.py        # In terminal 2 (open http://localhost:5000)

Test with dummy signal:

bashcurl -X POST http://localhost:8765/signal \
  -H "Content-Type: application/json" \
  -d '{"action":"LONG","instrument":"MES 09-26","quantity":1}'

You should see:


Signal logged in OrderRouter.log
Order appears in NT8's Orders tab
Fill comes back within 1-2 seconds
Dashboard updates showing the trade


Expected workflow


BarBridge writes a bar to CSV every bar close
live_runner reads CSV, runs ORB logic, posts signal if triggered
OrderRouter receives signal, places order in Sim101
NT8 fills the order
Dashboard shows everything
Logs capture every step


What this teaches you

The local bridge proves the rails work end-to-end:


Bars flow in ✓
Signals fire when expected ✓
Orders execute ✓
Fills come back ✓
Everything is logged ✓


Paper-trade on demo for 3-5 sessions. Verify live trades match backtest expectations exactly. If they do, the system is trustworthy.

Do NOT move to production (Railway) until all 5 checkmarks pass.
