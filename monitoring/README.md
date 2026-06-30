Monitoring Module (ASM + Alerts)

Your agent builds the observability layer here. Two files:


asm_dashboard.py — web UI showing system state (equity, drawdown, trades, positions)
telegram_alerts.py — Telegram bot wiring (optional)


This runs alongside your system and lets you understand what's happening without watching charts.

What your agent builds

Prompt for your agent:


Build the monitoring layer:

File: asm_dashboard.py (Flask web UI)


Read from logs/runner.log + NT8-Logs/OrderRouter.log + Supabase (once deployed)
Show pages:

/strategies — per-strategy state, P&L, trades
/accounts — per-account equity curve, drawdown headroom, daily loss
/signals — signal history, entry/exit prices, slippage
/portfolio — net position across all strategies + accounts
/ops — connection status, feed health, last update time



Refresh every 5 seconds
Run on http://localhost:5001


File: telegram_alerts.py (optional)


Subscribe to signal stream (from logs or Supabase later)
Send Telegram message on: new fill, error, drawdown approaching limit
Read TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID from .env
Run as background process or cron job




How to use

Local (logs-based):

bashpython asm_dashboard.py     # Open http://localhost:5001
python telegram_alerts.py   # Optional alerts

Production (Supabase-based):
After Supabase + Railway setup, asm_dashboard queries Supabase directly for live data.

What you'll see

Main dashboard:


Equity curve (real-time, updated on every fill)
Current drawdown % vs. daily limit (red if approaching)
Today's P&L + daily loss counter
Win rate + R-multiple distribution
Recent trades table
Connection status light


Alerts (if Telegram enabled):


"Entry: LONG MES 1 @ 5100.50"
"Exit: LONG MES 1 @ 5102.00 +$75 PnL"
"ERROR: No fill received for signal 42 (5+ min timeout)"
"WARNING: Drawdown at 95% of daily limit"


When to deploy this

Phase 1 (local, logs-based): Can deploy immediately after backtest + bridge tests pass. Just reads log files.

Phase 2 (production, Supabase-based): Deploy after you wire Supabase + Railway. Then ASM has live data.

Why monitoring matters

When you're running live, you're NOT watching charts. You trust the system. The monitoring layer keeps you informed:


Did the trade execute?
What's the current drawdown?
Is the feed still alive?
Did something break?


Your phone gets notified. You check the dashboard if needed. That's it.