# API Automation — Railway Services & Live Automation

The scheduled jobs, webhook handlers, and always-on workers that run on Railway + VPS. A live trading system runs 24/5 — automation is what fills the gap between "strategy fires" and "I'm asleep."

---

## The Services You'll Run

Two hosts handle automation: **Railway** for Python services + crons, **Windows VPS Task Scheduler** for NT8 lifecycle.

| Service | Host | Cadence | Purpose |
| --- | --- | --- | --- |
| Webhook backend (FastAPI) | Railway worker | Always on | Receives bars + fills from NT8, writes to Supabase |
| Python brain (live_runner) | Railway worker | Always on | Strategy evaluation, gate chain, routing |
| Telegram alerter | Railway worker | Always on | Subscribes to Supabase events, pushes to Telegram |
| Account snapshot | Railway cron | Every 15 min (market hours) | Pull broker balances → account_snapshots |
| Reconciliation sweep | Railway cron | Every 15 min | Compare NT8 positions to Supabase view |
| Daily digest | Railway cron | 17:15 ET | W/L + R per strategy to Telegram |
| Weekly recap | Railway cron | Sun 17:00 ET | Week aggregate |
| Drift monitor | Railway cron | Daily after close | Live vs backtest AUC, per-tier WR |
| Retrainer (ML) | Railway cron | Sun 02:00 UTC | Walk-forward retrain on live trades |
| NT8 stop/start/watchdog | VPS Task Scheduler | 16:55 / 17:10 / every 5 min | NT8 lifecycle |

Build them in order. Webhook backend + brain are critical-path; everything else is downstream.

---

## Universal Patterns (apply to every service)

Four patterns show up in every service. Bake them in from the start.

### 1. Idempotency

Every service can fire twice — network retries, Railway restart, manual replay. Every write must assume it might be called again.

**Pattern:** include a unique key per operation, check "have I done this before" via Supabase `idempotency_keys` table before acting. For crons: key on `(job_name, run_date)`. For webhooks: key on `(signal_id, account, fill_time)`.

### 2. HMAC Verification

Every public endpoint (anything NT8 POSTs to) must verify HMAC. Without it, anyone with your Railway URL can POST fake fills and crash your P&L tracking.

**Pattern:** sender includes `X-Signature` header = HMAC-SHA256(payload, shared_secret). Receiver re-computes and compares. Reject 401 on mismatch. Add timestamp in payload, reject if > 60s old (replay protection).

### 3. Healthchecks Pings

External heartbeat. Without it, a silently-failed cron looks identical to a healthy one until you notice missing data days later.

**Pattern:** every cron pings Healthchecks.io on success. Healthchecks alerts when the expected ping doesn't arrive. Free tier covers ~10 checks.

### 4. Fail-open for non-critical-path

If the Telegram alerter or Discord webhook is down, trading must keep running. Non-critical-path services must NEVER raise into the brain or backend.

**Pattern:** `try / except / log` wraps every external call. The trade-routing critical path never awaits a Telegram send.

---

## Webhook Backend (FastAPI on Railway)

The receiver for everything NT8 pushes. Three endpoints, HMAC-verified, quick-ack pattern.

Three endpoints:
- `POST /nt8/bar` — receives bar events from BarBridge
- `POST /nt8/fill` — receives fill events from OrderRouter
- `POST /nt8/snapshot` — receives balance snapshots

Each endpoint:
- Verifies HMAC signature via `X-Signature` header against env var `WEBHOOK_SECRET`
- Rejects 401 on bad signature
- Verifies timestamp in payload is < 60s old (replay protection)
- Quick-ack (returns 200 within 200ms), async-processes the Supabase write
- Dedups via `idempotency_keys` table
- Logs every received request to `webhook_events` table

Single FastAPI app, single Railway service.

---

## Account Snapshot Cron

Every 15 min during market hours, pull broker balances per account, write to `account_snapshots`. Powers the drawdown monitor + the dashboard's "today's P&L per account" view.

Every 15 minutes:
- Hits the NT8 bridge's `/router/account-state` endpoint
- For each account, captures: balance, equity, open positions, today's realized P&L, distance from trailing DD line
- Writes one row per account to Supabase `account_snapshots`
- Runs every 15 minutes during market hours, hourly outside
- Idempotent via `(account, ts_minute)` dedup
- Pings Healthchecks.io on success

---

## Reconciliation Sweep

Every 15 min during market hours, compare NT8's view of open positions against Supabase's view of "what should be open right now." Catches dropped webhooks, missed events, race conditions.

Every 15 minutes:
- GETs NT8 bridge's `/positions` endpoint (currently-open positions per account)
- Queries Supabase: per account, per strategy_id, what positions SHOULD be open
- Compares the two sets; for any discrepancy, write a `reconciliation` row
- High-severity discrepancy → critical event for Telegram alerting
- Auto-correct stale Supabase rows; NEVER auto-correct broker positions (manual review only)
- Direction is always **toward the broker as truth**

---

## Daily Digest + Weekly Recap

Daily fires 17:15 ET (Telegram + premium-Discord perf summary). Sunday 17:00 ET fires the weekly recap. EOD recap at 16:55 ET.

Dedup keyed on `(report_type, date)` in `trade_report_notification_log`. Single service handles all of them.

---

## Drift Monitor (ML strategies)

Daily after close, compare live AUC and per-tier WR to training baselines. If drift exceeds thresholds, write an operational event so it surfaces in Telegram + dashboard.

Daily after market close:
- Queries Supabase for last 30 days of scored signals
- Computes rolling AUC, rolling per-tier WR, rolling score distribution mean
- Compares to training-time baselines (stored in `models/<strategy>_manifest.json`)
- If drift exceeds thresholds (AUC drop > 0.03, tier WR gap > 5pp), write a critical event
- Telegram alert routes the event to operations channel

---

## Retrainer (ML strategies)

Sunday 02:00 UTC. Pull last week's settled trades, append to training set, run the walk-forward harness, gate-check the new model, replace the active model **only if every gate passes**.

**The gate is the most important step.** A fresh model is not automatically better. Shipping every retrain blindly accumulates drift damage.

Sunday 02:00 UTC:
- Appends last week's settled trades to training set
- Runs the full walk-forward pipeline
- Runs model gates to validate the candidate model
- If all gates pass: replace active model, log as `info`
- If any gate fails: keep old model, log as `operational` with details, do NOT auto-replace

---

## NT8 Lifecycle Tasks (Windows VPS)

Not Railway. Run on the VPS via Task Scheduler. See VPS_SETUP.md for PowerShell scripts:

- `NT8_Stop` — daily 16:55 ET
- `NT8_Start` — daily 17:10 ET
- `NT8_Watchdog` — every 5 min, 06:00–23:00 ET

---

## What's NOT Real Automation

- **Auto-tuning strategy parameters live** — no. Tuning is human-supervised, not continuous.
- **Auto-enabling new strategies** — no. Code shouldn't decide to ship.
- **Auto-scaling position size based on recent PnL** — tempting, dangerous. Vol-adjusted sizing is fine; pure PnL-based scaling chases regimes.