Strategies Module

Your agent builds strategy templates here. One working example + four stubs:


orb.py — working ORB logic (your agent copied from backtest)
klbs_template.py — KLBS stub (you research the parameters)
ib50_template.py — IB50 stub
tom_template.py — TOM stub
mgc_orb_template.py — MGC ORB stub


What your agent builds

Prompt for your agent:


Build strategy templates:

File: orb.py


Copy the ORB logic from backtest_orb.py into a reusable function
Function signature: def run_orb(df: pd.DataFrame, position_state: dict) -> dict
Input: df with OHLCV + index as timestamp, current position state
Output: dict with {action: "LONG"|"SHORT"|"FLAT", confidence: 0-1}
Use the exact same rules as backtest (opening range, 30-min window, break logic, times)
Comment everything


Files: klbs_template.py, ib50_template.py, tom_template.py, mgc_orb_template.py


Create function stubs for each: def run_klbs(df, position_state) -> dict, etc.
Read the framework docs in /docs/KLBS_framework.md (etc) to understand the concept
Leave comments explaining WHAT the strategy should do, but DON'T implement it yet
Example for KLBS:
def run_klbs(df, position_state):
    # KLBS logic (from framework):
    # 1. Identify key levels (PDH, PDL, PMH, PML, LPH, LPL)
    # 2. Fade exhaustion when price stretches too far from a level
    # 3. Entry: next bar's open after signal
    # 4. Stop: X points below/above key level
    # 5. Target: Y points in profit direction
    # TODO: Implement parameter research phase
    return {action: "FLAT", confidence: 0}




Each stub is a TODO for the human to research.



How to use

For backtest:

pythonfrom strategies.orb import run_orb

for i in range(50, len(df)):
    bar_history = df[:i+1]
    signal = run_orb(bar_history, position_state)
    # Process signal...

For live:

pythonfrom strategies.orb import run_orb

while True:
    # Read new bar from CSV
    signal = run_orb(bar_history, position_state)
    if signal['action'] != 'FLAT':
        # Post to OrderRouter

Research phase (YOU do this)


Pick one framework from /docs (e.g., KLBS)
Read the framework doc + RESEARCH_PROCESSES.md + STRATEGY_DEVELOPMENT.md
Fill in the stub with your parameters
Backtest it (using backtest_orb.py as template)
Walk-forward validate it
When edge is real, deploy it


Parameters to research

Each framework has a set of tunable parameters. Examples:

KLBS:


Which key levels (PDH, PDL, PMH, PML, LPH, LPL)?
Fade threshold (how far is "too far")?
Stop distance (how many points)?
Target distance (profit target)?
ML filter threshold (if using)?


IB50:


Initial balance window (how many minutes)?
Fade threshold (% of IB range)?
Retracement levels?


TOM:


Turn-of-month date range?
Which instruments show the effect most?
Time-of-day windows?


MGC ORB:


Opening range window (how many minutes)?
Break confirmation (how many ticks)?
Daily hold / exit times?


Your agent provides the template + logic structure. You research the parameters using the walk-forward methodology in /docs/RESEARCH_PROCESSES.md.

Example: How to research KLBS


Start with rough params (from Notion docs or intuition)
Backtest on 2021-2023 data
Walk-forward validate on 2023-2026 data
Check profit factor, max drawdown, Sharpe
Tweak params based on failures
Repeat until consistent edge shows up
Deploy to paper / sim
When live matches backtest, deploy to eval account


This is weeks to months of work. The framework is free. The edge is yours to find.