Research & Strategy Frameworks

This folder is where you learn how to find real edge. Three parts:

Part 1: The research process (read first)


RESEARCH_PROCESSES.md — walk-forward validation, OOF labels, honest backtesting, how to catch bullshit
STRATEGY_DEVELOPMENT.md — the 8-stage pipeline from idea to live deployment


Read these in order. They're not theory — they're the exact methodology used to validate every strategy in this system.

Part 2: Four strategy frameworks

These are the archetypes. Pick one. Research it. Find your own parameters.


KLBS_framework.md — Key-level mean reversion. Fade exhaustion when price stretches too far from a level it respects.
IB50_framework.md — Initial Balance Retracement. Fade extreme moves in the first hour.
TOM_framework.md — Turn-of-Month. Exploit intraday inefficiencies at month boundaries.
MGC_ORB_framework.md — Time-of-Day Opening Range Breakout. Trade the micro gold opening range.


Each framework doc explains:


The concept (why it should work structurally)
The logic (what you're looking for in price action)
The research prompt (starting point for your backtest)


What it does NOT include: Exact parameters. Those are yours to research.

Part 3: Advanced topics (reference)


ML_SIGNAL_PROCESSING.md — adding a machine learning filter on top of rule-based strategies (read AFTER you have validated edge)


How to use these

Step 1: Pick a framework

Read one of the four. Understand the concept. Ask yourself: "Does this make structural sense?"

Step 2: Research parameters

Use STRATEGY_DEVELOPMENT.md as your checklist. Go through stages 0-4:


Stage 0: Sanity (does the logic make sense?)
Stage 1: Data (is your data clean?)
Stage 2: Baseline (does raw logic show signal?)
Stage 3: Parameters (what params pass walk-forward?)
Stage 4: Slippage (does it survive realistic fees?)


Step 3: Validate on paper

Once you pass walk-forward on stages 0-4, paper-trade it on demo for 2-3 weeks. Verify backtest assumptions match live fills.

Step 4: Deploy

When live matches backtest + you have consistent edge (Profit Factor > 1.3, positive expectancy across 90%+ of folds), you're ready for a prop account eval.

Key principles

Most ideas should die in testing. That's the discipline working. If every idea works, you're not auditing hard enough.

Walk-forward validation is non-negotiable. If your strategy only works on the exact data you trained it on, it's curve-fit garbage. Stages 3 + 4 in STRATEGY_DEVELOPMENT.md enforce this.

Backtest numbers need auditing. Same-bar fills and look-ahead bias are silent killers. RESEARCH_PROCESSES.md shows you how to catch them.

Live results should match backtest closely. If they don't, something is wrong with your assumptions (slippage, timing, fill prices, position sizing). Debug before scaling.

Timeline expectations


Stage 0-2: Days (sanity check + baseline)
Stage 3: Weeks (parameter tuning via walk-forward)
Stage 4: Days (slippage validation)
Stage 5 (paper trade): 2-3 weeks
Stage 6+ (deployment): After all prior stages pass


This is not fast. Expect 1-3 months per strategy from idea to live deployment. That's normal. Anyone promising faster is selling something.

Getting stuck?


Backtest numbers look too good? → Read RESEARCH_PROCESSES.md, run lie-detector
Walk-forward results are inconsistent? → Read Stage 3 in STRATEGY_DEVELOPMENT.md
Live fills don't match backtest? → Read Stage 5 (Paper Trading) in STRATEGY_DEVELOPMENT.md
Drawdown is too high? → Read RISK_CONTROLS.md in /infra


Next steps


Pick a framework (suggest: KLBS or IB50, easiest to research)
Read STRATEGY_DEVELOPMENT.md
Run through stages 0-4 using the framework
Once edge is validated, ask your agent to help deploy to paper/sim (it'll help with the code side)
Paper-trade 2-3 weeks
Move to eval account


Good luck. The edge is in the research, not the code.
