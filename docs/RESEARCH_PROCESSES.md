Research Processes — Walk-Forward, OOF Labels, And Honest Backtesting

The difference between a strategy that works and one that's curve-fit garbage is methodology. This is that methodology.

The core problem

AI will confidently give you a backtest with:


75% win rate
Sharpe ratio of 4
Max drawdown of only $500


And it's all fake. Two silent killers:


Same-bar fills — strategy "decides" on bar N, fills on bar N's close (using future info)
Look-ahead bias — strategy peeks at data that wasn't available at decision time


Your job: catch these before you risk money.

Part 1: The Lie-Detection Pass

Before you trust ANY backtest, run two audits. Takes 30 seconds.

Audit 1: Same-bar fills

The bug: Strategy fires a signal on bar N's close, then fills itself on the same bar's close. Uses outcome info that didn't exist when the decision was made.

Correct pattern:


Signal fires on bar N (comparing history up to bar N)
Fill happens on bar N+1's open (first price after the signal)
Never use data from bar N's future (close, high, low after the decision point)


How to catch it:
Ask your agent to audit the code:


For every place a fill price is set in backtest_orb.py, show me the line and explain whether it uses data from the signal bar or a later bar. Flag any that use same-bar data as a bug.



Audit 2: Look-ahead bias

The bug: Strategy uses information that wasn't available at the point of decision.


Indexing df.iloc[i+5] inside a per-bar loop (five bars into the future)
Calling df['close'].max() across the entire series and treating it as "resistance" (max so far)
Using df[df['close'] > X] where X is calculated from future bars


How to catch it:


Audit backtest_orb.py for look-ahead bias. List any places the strategy uses data from a future bar, or aggregates the entire series in a way that wouldn't have been available at decision time.



If both audits pass: Your numbers are real (probably bad, but real). Move on.

If either fails: Stop. Fix the bug. Re-run backtest. The numbers you had were fiction.

Part 2: Walk-Forward Validation

One backtest is useless. You need multiple backtests across different time periods to prove the strategy works across regimes.

What is walk-forward?

You divide your historical data into non-overlapping windows (regimes). For each window:


Train window: Learn parameters on this period
Test window: Validate on the NEXT period (out-of-sample)
Move forward, repeat


Example with 5-year data (Jan 2021 - Jan 2026):

Window 1: Train on 2021-Q1, Test on 2021-Q2
Window 2: Train on 2021-Q2, Test on 2021-Q3
Window 3: Train on 2021-Q3, Test on 2021-Q4
... repeat until end of data ...
Window 20: Train on 2025-Q4, Test on 2026-Q1

Why this matters:


Single train/test split can be lucky (picked the easiest period to trade)
Walk-forward across 20 windows shows the strategy works in diverse market conditions
If 18/20 windows are profitable, the edge is real
If only 5/20 are profitable, it's curve-fit garbage


The checklist

After you run a walk-forward backtest, check these boxes:


 Total trades across all windows: > 100 (more = more confidence)
 Out-of-sample profit factor: > 1.3 (target 1.5+)
 Win rate on OOS: > 50% (lower is okay if R-multiple is good)
 Profit factor on OOS positive in 90%+ of folds (at least 18/20 windows)
 Max drawdown acceptable (fits inside your prop firm's rule)
 Results don't degrade when you apply realistic slippage (1-2 tick worse)
 Sharpe ratio on OOS: > 0.8 (target 1.0+)


If all boxes check: Real edge. Ready for paper-trading.

If any box fails: Either the edge isn't there, or you're curve-fitting. Research more or kill the strategy.

Part 3: Out-of-Sample (OOF) Labels

When you run walk-forward, you get two sets of labels:


In-sample (IS): Trained on this data
Out-of-sample (OOS): Never trained on this data


Critical rule: Report OOS numbers, not IS.

IS numbers will ALWAYS look better. That's expected. The question is: do the OOS numbers prove edge?

If IS win rate is 65% but OOS is 35%, the 65% is fake (curve-fit). Report 35%.

Part 4: Slippage Stress Test

Backtest assumes you fill at the NEXT bar's open. Reality:


Entry slippage: 1-2 ticks worse (you're a market taker)
Exit slippage: 1-2 ticks worse
Commission: $0.62 round-turn per contract (NT8)


The stress test:


Run backtest with realistic slippage + commission
P&L should still be positive on OOS
If P&L turns negative under slippage, the edge is too thin


How to test:
In backtest, apply 1 tick slippage on every entry + exit, and $0.62 commission. Re-run. Does it still pass walk-forward?

Part 5: Regime Breakdown

Market conditions change. Mean-reversion works great in choppy markets, breaks in strong trends. Breakout works great in trending markets, breaks in chop.

Optional deep-dive: Breakdown your walk-forward results by regime (bull, bear, high vol, low vol). Does the strategy degrade in any regime?

If it does, you have two options:


Add a regime filter (don't trade in bad regimes)
Accept lower returns in some regimes


Part 6: The Research Prompt (for your agent)

When you're ready to backtest a new strategy, give your agent this:


Build a walk-forward backtest for [STRATEGY NAME]:


Load historical 1-minute bars from data/MES_1m.parquet
Divide data into 20 non-overlapping windows (quarterly, 2021-2026)
For each window:

Train: Run strategy on first 75% of window, optimize parameters
Test: Run strategy on last 25% of window (out-of-sample), DO NOT tune



Aggregate results: total trades, win rate, PF, Sharpe, max DD across all OOS windows
Output:

output/[STRATEGY]_walkforward.csv with one row per window (trades, PF, wins)
Summary stats (total OOS trades, average PF, % windows profitable)
Warning if PF < 1.3 or < 90% windows profitable







Then audit the results against Part 3 checklist.

When you're stuck

Backtest numbers look too good?
→ Run lie-detector (Part 1), then check slippage stress (Part 4)

Walk-forward results are inconsistent across windows?
→ Strategy is sensitive to regime. Add regime filter or accept variability.

Live results don't match backtest?
→ Assumption mismatch (fill prices, timing, position sizing). Debug in paper-trading before scaling.

Drawdown is too high?
→ Re-read RISK_CONTROLS in /infra. You need position sizing rules.

Key principles

Report OOS, not IS. In-sample is your training set. Out-of-sample is your reality check.

20 windows minimum. 5-10 windows is not enough. 20+ windows proves the edge across different market conditions.

Slippage is real. Your backtest fill at next bar's open. Live, you're 1-2 ticks worse. Build it in.

If edge is real, it shows up in walk-forward. If you're chasing 18/20 windows profitable, you have edge. If it's 10/20, you're guessing.

Most strategies fail here. This is the gate. Most ideas should die at walk-forward validation. If every idea passes, you're not auditing hard enough.
