# KLBS Framework

## 1. Framework Name & Concept

KLBS is a rule-based mean-reversion system for US equity index futures (MES and MNQ). It trades rejection of structurally important intraday and overnight reference levels. The core assumption is that most tested levels in liquid index markets are *not accepted immediately*, and instead produce short-term mean reversion before any potential continuation.

The strategy is explicitly contrarian: it does not follow breakouts, it fades failed attempts at acceptance around known liquidity pools.

---

## 2. Why It Works

The edge is driven by microstructure behaviour around widely observed price levels:

- Stop clustering above/below prior session extremes
- Liquidity sweeps during session transitions
- Passive liquidity replenishment after initial volatility bursts
- Mean reversion tendency in index futures during non-trend regimes

The inefficiency is not directional prediction, but *overreaction and retracement behaviour* around predictable liquidity zones.

---

## 3. Key Concepts

### Reference Levels
- PDH / PDL: Previous Day High/Low
- PMH / PML: Pre-market High/Low
- LPH / LPL: London session high/low

### Rejection Logic
- Wick through level + close back inside range
- Failure to sustain beyond level after break attempt
- Absorption signatures (price stalls at level after sweep)

### Filters
- Session filter (avoid low-liquidity periods)
- Distance-to-level filter
- Volatility regime filter (ATR-based or similar)
- ML probability overlay

---

## 4. The Trade

### Entry
- Price approaches key level
- Rejection pattern confirms failure of breakout
- Entry is placed in the opposite direction of attempted breakout

### Stop
- Beyond level + buffer (tick-based or ATR-based)

### Target
- Mean reversion toward local equilibrium (mid-range or opposite liquidity zone)

### Exit
- Fixed bracket OR session-based exit
- Forced flat at session end

---

## 5. Parameters to Research

- Which levels contribute positive expectancy
- Optimal rejection definition (wick size, close threshold)
- Distance-to-level entry threshold
- Volatility regime filter boundaries
- Session inclusion/exclusion windows
- Stop buffer sizing per instrument
- Target methodology (fixed, ATR, or level-based)
- ML model features and thresholds
- Trade frequency caps per session

---

## 6. AI Research Prompt

> Build a research pipeline for KLBS using 1-minute MES/MNQ data.
>
> Identify PDH/PDL, PMH/PML, LPH/LPL per session.
> Detect rejection events using wick penetration and close-back criteria.
> Label trades as successful if mean reversion of X ticks occurs within Y bars.
>
> Perform walk-forward optimisation using 12-month training and 6-month OOS windows.
> Evaluate:
> - Expectancy
> - Profit factor
> - Drawdown stability
> - Regime sensitivity
>
> Compare:
> - Level-only strategy
> - Level + rejection filter
> - Level + rejection + ML filter
>
> Output optimal parameter set and stability heatmaps.

---

## 7. When It Breaks

- Strong trend regimes (macro-driven directional markets)
- News shock sessions with persistent breakout continuation
- Low-liquidity periods where spreads dominate signals
- Overfitted level definitions (too many false positives)

---

## 8. Typical Performance

Observed characteristics in properly tuned systems:

- Win rate: 45–60%
- Profit factor: 1.2–1.6
- Moderate drawdowns during trend regimes
- High trade frequency relative to directional systems

---

## 9. How We Know It Works

Validation relies on:

- Walk-forward testing across multiple volatility regimes
- Out-of-sample confirmation across instruments (MES, MNQ)
- Sensitivity analysis on level definitions
- Slippage and execution simulation
- Stability of expectancy across folds rather than single optimised runs