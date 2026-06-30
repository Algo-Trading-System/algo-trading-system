# Getting Started

You've cloned the repo and you're reading this. Good.

## Step 1: Set up your API keys (5 minutes)

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Now open `.env` and fill in 3 API keys. Here's what each one is and where to get it:

### DATABENTO_API_KEY

**What it is:** Databento is where you fetch historical price data (5 years of 1-minute bars for backtesting). You need their API key to download this data.

**Where to get it:**
1. Go to https://databento.com
2. Sign up (free, takes 30 seconds)
3. They give you $500 in free credits (more than enough for this project)
4. Copy your API key from your account dashboard
5. Paste into `.env` next to `DATABENTO_API_KEY=`

**Why you need it:** You can't backtest without data. Databento is cheap and reliable.

### WEBHOOK_SECRET

**What it is:** A secret password that your system uses to verify messages between different parts. Think of it like a secret handshake between your NinjaTrader chart and your Python code. Only someone who knows the secret can send messages.

**How to generate it:** Use any random 32-character string. You can:
- Run this in terminal: `python -c "import secrets; print(secrets.token_hex(16))"` (generates a 32-char string)
- Or just pick one yourself, like: `my-super-secret-webhook-key-12345678`

**Why you need it:** Security. When signals fire and orders are placed, you want to make sure it's YOUR system doing it, not someone else's.

### TELEGRAM_BOT_TOKEN (optional)

**What it is:** Your personal Telegram bot that sends you alerts. When a trade executes, when drawdown is high, when something breaks — your phone gets a message. Optional, but nice to have.

**How to get it (only if you want alerts):**
1. Open Telegram (app or telegram.org)
2. Search for "BotFather" (official Telegram bot manager)
3. Type `/start`, then `/newbot`
4. Give your bot a name (e.g., "MyTradingBot")
5. BotFather gives you a token. Copy it.
6. Paste into `.env` next to `TELEGRAM_BOT_TOKEN=`

Also find your Telegram user ID:
1. Search for "userinfobot"
2. Type `/start`
3. It shows your user ID
4. Paste into `.env` next to `TELEGRAM_CHAT_ID=`

**Why you need it:** You won't watch charts all day. Telegram tells you when something happens.

---

## Step 2: Give your agent this prompt

Now you have `.env` set up. Open Claude Code and paste this:

```
Read memory.md and goals.md in the repo root. Then build the entire system end-to-end:

1. Follow the file structure (backtest/ bridge/ strategies/ infra/ monitoring/ docs/)
2. For each folder, read the README.md — it tells you what to build
3. When done, I should be able to run: python backtest_orb.py (see results), then python live_runner.py (paper-trade on demo)
```

Your agent reads the docs, builds the code, and delivers a working system in 1-2 hours.

---

## Step 3: While your agent builds

- Create free accounts on Databento (already done), Railway, Supabase
- If you set up Telegram, open Telegram and start a chat with your bot (just type something)
- Get your NinjaTrader demo credentials

---

## Step 4: After the build

You have a working backtest, strategy templates, and the bridge (Python ↔ NinjaTrader) wired.

**Now read:** `/docs/STRATEGY_DEVELOPMENT.md` (8-stage pipeline) and `/docs/RESEARCH_PROCESSES.md` (walk-forward validation).

Pick one framework (KLBS, IB50, TOM, or MGC ORB). Research it. Find your edge.

---

## Next steps

1. Follow `/backtest/README.md` — agent builds backtest + lie-detector
2. Follow `/bridge/README.md` — agent builds bridge (BarBridge, OrderRouter, live_runner, dashboard)
3. Follow `/strategies/README.md` — agent builds strategy templates
4. Paper-trade on demo for 3-5 sessions
5. Research edge using the frameworks (weeks to months)
6. Deploy to eval account when edge is real

---

That's it. Build it. Own it.