# TOM Framework (Turn of Month)

## 1. Framework Name & Concept

Turn of Month (TOM) is a calendar-based long-only equity index futures strategy that exploits systematic return bias around the transition between calendar months.

Unlike price-reactive strategies, TOM is purely time-driven: the decision to trade is determined entirely by the trading calendar.

---

## 2. Why It Works

The edge is driven by recurring institutional cashflow mechanics:

- Pension and retirement contributions
- Mutual fund inflows at month-start
- Portfolio rebalancing cycles
- Benchmark tracking adjustments
- Systematic allocation schedules

These flows create a persistent tendency for equity indices to exhibit positive drift around month boundaries.

The inefficiency is structural: predictable capital inflow timing vs fragmented market execution.

---

## 3. Key Concepts

### Trading-Day Rank
- Position of current day within monthly trading cycle
- Includes handling of holidays and partial months

### TOM Window
- Last N trading days of prior month
- First M trading days of new month

### Instrument-Specific Calibration
- MES, MNQ, MGC each have distinct validated windows
- No universal calendar applies across assets

---

## 4. The Trade

### Entry
- Enter long at 09:30 ET RTH open on valid TOM days
- No price condition required

### Stop
- Fixed hard stop (instrument dependent)
- Executed immediately at entry

### Exit
- Forced exit at 16:00 ET
- No discretion-based exits

### Constraints
- One trade per instrument per day
- Long-only exposure
- No re-entry after stop-out

---

## 5. Parameters to Research

- Optimal TOM window (N last days / M first days)
- Instrument-specific eligibility rules
- Inclusion of last trading day of prior month
- Stop size calibration per volatility regime
- Position sizing methodology
- Holiday adjustment effects
- Volatility filtering (optional exclusion of extreme regimes)
- Interaction with macro events

---

## 6. AI Research Prompt

> Build a backtesting system for a Turn-of-Month strategy.
>
> Data:
> - 10+ years of daily MES/MNQ/MGC data
>
> Steps:
> 1. Identify monthly boundaries
> 2. Construct TOM windows:
>    - Last N trading days of month
>    - First M trading days of next month
> 3. Simulate entry at next-day open
> 4. Apply fixed stop and end-of-day exit
>
> Variants to test:
> - Momentum TOM (only trade after positive prior month)
> - Mean-reversion TOM (only after negative prior month)
> - Volatility-filtered TOM
>
> Evaluation:
> - Expectancy
> - Sharpe ratio
> - Drawdown profile
> - Cross-instrument consistency
>
> Use walk-forward validation (3-year train / 1-year test).

---

## 7. When It Breaks

- Structural regime shifts in institutional flow behaviour
- High-volatility macro shock periods
- Strong trend continuation environments where early-month reversal fails
- Calendar distortions from holiday clustering

---

## 8. Typical Performance

Observed characteristics:

- Low frequency, high consistency edge
- Modest per-trade expectancy
- Stable Sharpe contribution when combined with intraday systems
- Lower drawdowns than intraday strategies

---

## 9. How We Know It Works

Validation is based on:

- Multi-decade historical testing (daily bars)
- Out-of-sample walk-forward analysis
- Comparison vs buy-and-hold baseline
- Regime segmentation (bull/bear/high-volatility)
- Cross-instrument consistency checks