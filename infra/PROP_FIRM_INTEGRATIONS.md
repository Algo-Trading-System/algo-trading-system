# Prop Firm Integrations — Connect NT8 to Your Eval

By the time you're here you should already have:

- A working end-to-end system on NT8 demo (GETTING_STARTED.md Steps 1-8)
- A strategy with verified edge from walk-forward research (RESEARCH_PROCESSES.md + STRATEGY_DEVELOPMENT.md)
- The monitoring layer running — Supabase + Telegram + ASM (GETTING_STARTED.md Step 10)

If any of those is missing, go back. Going to a prop eval without verified edge is just lighting eval fees on fire.

This doc covers: confirming the firm allows algos, the NT8 connection, encoding firm rules as code, account groups, eval discipline, scaling to multi-firm.

---

## Recommended Firms

Currently using **Lucid** and **Tradeify**. Both confirmed algo-friendly. Both Rithmic-routed (so a single NT8 install on one VPS handles both, plus any other Rithmic-routed firm you add later).

Plenty of other futures firms exist — some allow algos, some don't, terms change. **Read the rules page before paying any eval fee.** Look for explicit language: "automated trading allowed," "EAs allowed," "algos permitted." If ambiguous, ask support and get a written answer.

---

## Why Multi-Firm Eventually

Most serious mechanical traders run accounts at **3-5 firms**.

- One firm changes rules / pauses payouts / has an outage → you don't lose your whole operation.
- Capital diversification across firms = capital diversification across rules + payout policies.

Cost is operational complexity (more rules to encode, more dashboards). Worth it once your first firm is stable.

---

## Step 1 — Account Sizing

From research + paper trading you know your strategy's worst-case drawdown. The account size must comfortably exceed it.

**Rule of thumb: 1.5× margin minimum.** If your strategy's honest observed max DD is $1,000, the firm's DD limit should be at least $1,500 — ideally more.

**Start with the smallest account that fits.** PT/DD ratios are more favourable on smaller accounts so the eval is easier to pass. Scale up after graduating + running stable at the smaller size.

Size down your strategy (fewer contracts) if needed to fit a smaller account. Don't size up to fit a bigger one.

---

## Step 2 — Connect NT8 to the Firm

Same mechanical flow as GETTING_STARTED.md Step 3, prop credentials instead of demo:

1. Get credentials from the firm's dashboard / welcome email.
2. NT8 Control Center → Connections → Configure → New.
3. **Connection provider:** what your firm tells you to use — usually `NinjaTrader`, sometimes `Rithmic` directly.
4. **Connection name:** name it after the firm (`Tradeify`, `Lucid`).
5. Paste credentials.
6. **Simulation mode** while you confirm setup. Switch to **Live** when you start the eval.
7. Save. Connect. Green light. Account visible in the Accounts tab.

**Why NT8 dominates prop futures:** almost every firm routes through Rithmic under the hood. One NT8 install on your VPS handles every Rithmic firm — one routing codebase, one workspace.

---

## Step 3 — Encode the Firm's Rules as Code

This is where mechanical prop trading actually lives. Every rule that could disqualify you needs to be enforced in code.

**Pattern: rule-as-code.** Each firm gets a config row in Supabase `account_config`. The brain reads it on every signal evaluation and applies the constraints.

### Example config row

```yaml
firm_name: Tradeify
account_group: tradeify
drawdown_type: eod_trailing
drawdown_amount: 2500
allowed_instruments: [MES, MNQ, MGC, MCL]
news_window_restrictions:
  - { event: high_impact, before_minutes: 2, after_minutes: 2 }
allow_overnight: false
min_trading_days: 3
profit_target: 1500
consistency_rule:
  max_single_day_pct_of_total: 0.5
payout:
  min_trading_days_before_request: 10
  min_balance_above_starting: 1000
```

### What needs encoding per firm

- **Drawdown type + amount** — EOD trailing vs intraday trailing vs static. Brain tracks distance from the line in real time. Auto-disable when within 5%.
- **Allowed instruments** — reject signals on instruments not whitelisted.
- **News-window restrictions** — block trading 2 min around high-impact news. Calendar from forexfactory loaded nightly.
- **Overnight / weekend holds** — force-flatten before close on accounts that don't allow holds.
- **Consistency rule** — many firms cap single-day P&L at X% of total profits. Brain tracks daily P&L distribution, blocks new signals if today's win would breach.
- **Payout-readiness gates** — don't request payouts if balance + trading days don't qualify.

---

## Step 4 — Account Groups (hedge + stack prevention per firm)

Multi-firm scaling needs per-group scoping:

- Each account belongs to an **account group** (typically one per firm: `lucid`, `tradeify`, etc.)
- Hedge / stack checks scoped to the group, NOT globally
- Orders can route to accounts in different groups in parallel
- Orders CANNOT create a hedge or stack within a single group

**Why per-firm boundary:** prop firms see hedges and stacks within THEIR accounts; they don't see what you're doing at other firms. The rule boundary is the firm boundary.

This lets you run KLBS-long MNQ on Lucid while running IB50-short MNQ on Tradeify simultaneously. Same combo within Lucid alone would be blocked.

---

## Step 5 — Per-Account, Per-Strategy Sizing

A $50K Tradeify account might trade 1 contract at a given tier; a $150K Lucid account might trade 3. A personal account might trade 5.

**Pattern:** per-account, per-strategy contract counts live in Supabase `account_config` (or in the ASM dashboard for live editing). Brain reads them at signal time; execution submits accordingly.

This lets you scale up accounts that perform without recompiling, and pull back accounts that wobble without touching the strategy.

### Personal money alongside prop

Personal account = just another account in your routing system. Has its own rules (or none, depending on broker). **Flagged as personal**, not prop, so reports can separate the two. Prop DD metrics + profit targets don't apply.

---

## Step 6 — Take the Eval (discipline)

With firm rules encoded + account size sized + monitoring layer running:

- **Trade exactly what you paper-traded.** Same strategy, same instruments, same size.
- **Don't add new instruments mid-eval.**
- **Don't increase size mid-eval.**
- **Don't override the system.** If it's not firing a trade you "would have taken," that's the discipline working.
- **Watch, don't intervene.** Manual overrides during eval are the #1 way to blow it.
- **Take your time.** Evals have a minimum-trading-days requirement but no upper timer. Don't rush.

---

## Step 7 — Scale to Multi-Firm (after one firm is stable)

1. Pass eval on firm 1, smallest account that fits.
2. Run on one account for 30+ live trades, confirm live matches paper.
3. Scale to a second account at the same firm (multiple accounts, same group).
4. Take payouts; confirm the payout flow works end-to-end.
5. **Only then** add firm 2 — second account group, same routing code, parallel deployment.
6. Document any per-firm code nuances before adding firm 3.

Operational diversification (3-5 firms) is the long-term goal. Getting there one firm at a time saves you from rebuilding the routing layer three times.

---

## Common Mistakes

- **Manual rule following** — "I'll remember not to trade during news." You won't. Encode it.
- **One firm forever** — first firm is a foothold. Diversifying across 2-3 firms is risk management.
- **Treating eval and funded identically** — different rules sometimes. Routing logic should know which is which.
- **Same SL distance on $25K and $150K accounts** — proportional risk only works if you size proportionally per account.