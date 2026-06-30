Backtest Module

Your agent builds the backtest harness here. Three files:


download_data.py — fetch 5 years of 1-min bars from Databento
backtest_orb.py — run the starter ORB strategy on historical bars
lie_detector.py — audit the backtest for same-bar fills + look-ahead bias


What your agent builds

Prompt for your agent:


Build the backtest harness for a simple opening-range breakout strategy:

File: download_data.py


Load DATABENTO_API_KEY from .env
Download 5 years of 1-minute OHLCV bars for MES continuous contract (MES.n.0 on GLBX.MDP3) from 2021-01-01 to 2026-01-01
Save as data/MES_1m.parquet (parquet, not CSV)
Print date range + row count when done


File: backtest_orb.py


Load data/MES_1m.parquet
Define opening range as high/low of first 30 min (9:30-10:00 ET)
If price breaks above range high after 10:00 ET → LONG at next bar's open
If price breaks below range low after 10:00 ET → SHORT at next bar's open
Stop loss: 5 points. Take profit: 10 points. Exit at 15:55 ET.
One trade per day max.
Commission: $0.62 round-turn. Slippage: 1 tick entry + 1 tick exit.
Output: output/orb_trades.csv (entry time, exit time, side, entry price, exit price, P&L)
Print summary stats: total trades, win rate, profit factor, Sharpe, max drawdown, expectancy per trade


File: lie_detector.py


Audit backtest_orb.py for:

Same-bar fills (strategy uses bar N's close to fill bar N — wrong)
Look-ahead bias (uses future data before decision time)



Report findings clearly: PASS or FAIL + specific issues




How to use

bashpython download_data.py          # Fetch data
python backtest_orb.py           # Run backtest
python lie_detector.py           # Audit the backtest

Expected output (ORB is unprofitable on purpose)

Total trades: ~1,000
Win rate: ~25%
Profit factor: < 1
Max drawdown: ~$2,500
Sharpe: < 1
Expectancy: negative

Then lie_detector.py should return:

Same-bar fill audit: PASS
Look-ahead bias audit: PASS

If either fails, the strategy isn't trustworthy. Stop and debug.

What this teaches you

The starter ORB loses money. That's intentional — you're not chasing day-one profit. You're proving:


Your data pipeline works
Your backtest numbers are honest
You can spot bullshit in AI-generated code


Once these three pass, the real work is research (Strategy Development + Research Processes in /docs).
