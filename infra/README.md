Infrastructure Module

This folder contains documentation + code for system setup. Three parts:

Part 1: Documentation (read these first)


ARCHITECTURE.md — system diagram + component overview
NT8_SETUP.md — NinjaTrader connection landscape + survival rules
VPS_SETUP.md — Windows VPS setup (Mac/Linux users only)
SUPABASE_SETUP.md — database schema + setup steps
TELEGRAM_SETUP.md — optional alerts wiring
RISK_CONTROLS.md — account-level circuit breakers
PROP_FIRM_INTEGRATIONS.md — connecting to Tradeify, FundedNext, etc. (post-deployment)
API_AUTOMATION.md — Railway backend + webhook patterns (reference)


Part 2: Code (your agent builds this later)


railway_webhook.py — FastAPI backend on Railway (production transport, not local)
supabase_schema.sql — database schema (DDL, agent loads this once)


Part 3: Configs


Sample .env values for each stage (demo → paper → eval → live)


Build order (for your agent)

Phase 1 (local/demo):


NT8 connection + demo credentials (manual, you do this)
BarBridge + OrderRouter (your agent built in /bridge)
Backtest harness (your agent built in /backtest)
live_runner + dashboard (your agent built in /bridge)


Phase 2 (if needed: Mac/Linux)


Follow VPS_SETUP.md
Install NT8 on VPS
RDP into VPS
Run everything there instead of localhost


Phase 3 (deployment):


Create Supabase project
Load supabase_schema.sql
Create Railway project
Your agent builds railway_webhook.py
Update BarBridge + OrderRouter to POST to Railway instead of CSV
Update live_runner to subscribe to Railway bar bus
Wire Telegram (optional)
Deploy ASM dashboard (optional)


Your agent's prompts

For Phase 1: Already handled by /backtest + /bridge README.md

For Phase 3: Read SUPABASE_SETUP.md + PROP_FIRM_INTEGRATIONS.md for the prompts.

What NOT to do


Don't hardcode API keys (use .env always)
Don't skip VPS setup if you're on Mac/Linux (NT8 is Windows-only)
Don't deploy to Railway before paper-trading locally passes all checks
Don't connect to a prop firm before you have validated edge + passing walk-forward