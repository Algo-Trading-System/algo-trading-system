Strategy Development — From Idea To Live

Every strategy you'll ever run goes through these 8 stages. This is your checklist.

Stage 0: Sanity

Question: Does this idea make structural sense?

Example: "KLBS fades exhaustion when price stretches too far from a key level."


Why? Mean reversion is real (price extremes revert, structurally sound)
When? Works in choppy/range-bound markets, breaks in strong trends
Entry: Price breaks a key level, then retraces back into it
Risk: Trend overpowers mean-reversion (need regime filter?)


Pass criteria:


You can explain the logic in one sentence
You understand why it should work (not just "backtests good")
You can name 2-3 market conditions where it should fail


Fail: Idea doesn't make structural sense → Kill it, move on


Stage 1: Data

Question: Is your data clean and realistic?

Checklist:


 Dates span your backtest period (no gaps)
 OHLCV columns are sensible (open < close, high ≥ both, low ≤ both, volume > 0)
 No missing data gaps during trading hours (> 10 min gap = bad)
 Timestamps are timezone-aware (assume ET for US futures)
 Slippage / commission built in (1 tick entry, 1 tick exit, $0.62 round-turn)


Tool: Your agent runs a data audit script that catches these.

Pass: Data is clean. Proceed.

Fail: Fix data or get better source → Then re-run


Stage 2: Baseline

Question: Does the raw logic show ANY signal?

Run a simple backtest with basic parameters (no tuning). Do trades fire? Does P&L wiggle at all?

Example for KLBS:


Use PDH/PDL (previous day high/low) as key levels
Fade threshold: 10 pips from level
Stop: 5 points, Target: 10 points
Run on 2021-2022 data (1 year, unoptimized)


Expected results (probably negative):


~500-1000 trades
Win rate: 40-60%
Profit factor: 0.8-1.1 (likely negative)
Purpose: Prove logic fires signals, not chase profit


Pass: Signals fire, system works end-to-end (backtest runs, orders placed, fills logged)

Fail: Logic doesn't generate signals → Debug and re-run


Stage 3: Parameters

Question: Can you find parameters that show consistent edge on out-of-sample data?

This is where you do walk-forward (RESEARCH_PROCESSES.md, Part 2).

Process:


Divide 5-year data into 20 quarterly windows
For each window: train on 75%, test on 25% (OOS)
Tune parameters to maximize win rate / Sharpe on training window
Measure results on OOS window (don't tune on this)
Repeat across all 20 windows
Aggregate OOS results


Pass criteria (OOS results only):


Total trades: > 100
Profit factor: > 1.3 (target 1.5+)
Win rate: > 50%
Positive in 90%+ of windows (18/20 folds)
Sharpe: > 0.8


Fail: Results degrade on OOS → Kill strategy or refine logic

Duration: Days to weeks (depends on how many parameters to tune)


Stage 4: Slippage

Question: Does edge survive realistic fees?

Re-run walk-forward with 1 tick entry slippage + 1 tick exit + $0.62 commission.

Pass criteria:


Profit factor still > 1.3 on OOS
Win rate still > 50%
No negative drift when slippage added


Fail: Edge disappears with slippage → Kill strategy

Duration: Days (just add slippage to existing backtest, re-run)


Stage 5: Paper Trading

Question: Does live trading match backtest assumptions?

Run strategy on demo for 2-3 weeks. Compare live results to backtest expectations.

Checklist:


 Win rate ≈ backtest (±5-10% variance okay, bigger = problem)
 Average P&L per trade ≈ backtest (±1-2 ticks for slippage, bigger = problem)
 Max drawdown within expectations
 No system crashes (stable for 6+ hour sessions)
 Fill prices within 1-2 ticks of next-bar-open assumption


Pass: Live matches backtest → Ready for eval

Fail: Live result ≠ backtest → Debug assumptions (slippage model, timing, position sizing, entry/exit logic)

Duration: 2-3 weeks (need at least 20-30 live trades for confidence)


Stage 6: Deployment

Question: Ready for real money?

At this point:


✓ Logic makes sense (Stage 0)
✓ Data is clean (Stage 1)
✓ Signals fire (Stage 2)
✓ Edge shows on walk-forward OOS (Stage 3)
✓ Edge survives slippage (Stage 4)
✓ Live matches backtest (Stage 5)


Next steps:


Connect NT8 to prop firm account
Configure position sizing + risk rules
Start on eval account (usually max $100k-$500k depending on firm)
Run for 20-30 days minimum


Typical eval rules (varies by firm):


Max daily loss: 2-3% of balance
Max drawdown: 5-10% of balance
Max contracts per trade: varies
Hold time: varies


Your job: Size positions so you never break these rules.


Stage 7: Scale

Question: Can you run this on multiple accounts?

Once eval passes and you get a funded account:


Replicate to 2nd, 3rd, 4th account
Monitor for consistency across accounts
Watch for correlation issues (all accounts bleeding at same time?)



Stage 8: Iterate

Question: Can you add more strategies?

Once you have 1 profitable strategy live, research a 2nd. Repeat Stages 0-6.

Build a portfolio of non-correlated strategies. Diversification across strategies = lower drawdown, smoother equity curve.


Checkpoint: What kills strategies

Most ideas fail at one of these points:

Stage 0: Logic doesn't make sense (kill early, save time)
Stage 2: Signals don't fire (implementation bug)
Stage 3: Can't find parameters that work OOS (idea isn't there)
Stage 4: Edge disappears with realistic slippage (too thin)
Stage 5: Live doesn't match backtest (fill assumptions wrong, timing wrong, sizing wrong)
Stage 6-7: Eval rules are too strict (can't size without blowing up)

If your strategy dies at Stage 3 or 4, that's normal. Shelve it. Idea wasn't as good as you thought.


Timeline expectations


Stage 0: Hours (sanity check)
Stage 1: Hours (data audit)
Stage 2: Days (baseline run)
Stage 3: Weeks (parameter tuning + walk-forward)
Stage 4: Days (slippage validation)
Stage 5: 2-3 weeks (paper trading)
Stage 6: 20-30 days (eval account)
Total: 2-4 months per strategy


That's normal. Anyone promising faster is lying.


Your AI agent's role

Your agent can automate Stages 1-4 (data → slippage validation). You do Stages 0, 5-8 (sanity, paper trading, deployment, iteration).

Prompt for your agent (Stages 1-4):


Build a complete research pipeline for [STRATEGY]:


Audit data: check dates, OHLCV sanity, gaps, timezone
Run baseline: simple parameters, 1 year backtest, log signals
Run walk-forward: 20 quarterly windows, train/test split, optimize on IS, report OOS
Add slippage: 1 tick entry, 1 tick exit, $0.62 commission, re-run walk-forward
Output CSV + summary stats. Pass/Fail on criteria: PF > 1.3, 18/20 windows profitable, Sharpe > 0.8




Agent builds the harness. You interpret results.


You're not done until all 8 stages pass

One more thing: most strategies die before live money. That's the gate doing its job. Better to kill 10 ideas in research than deploy 1 bad one on an eval account.

When you find one that passes all 8 stages, you have something real. Build on that.