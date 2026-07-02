# IB50 Framework

## 1. Framework Name & Concept

IB50 is a retracement-based continuation strategy built around the Initial Balance (IB) of a trading session. It avoids chasing initial breakouts and instead waits for price to retrace into the IB after a confirmed directional expansion.

The core idea: early session breakouts are often incomplete moves. IB50 seeks improved entry price on the retracement phase of that same directional expansion.

---

## 2. Why It Works

The edge comes from intraday auction behaviour:

- Initial Balance defines early session fair value discovery
- Breakouts often trigger liquidity grabs and stop runs
- Institutional execution frequently requires retracement for size accumulation
- Momentum continuation often resumes after shallow pullbacks

The inefficiency is the *delayed entry requirement of large participants*, which produces retracement liquidity.

---

## 3. Key Concepts

### Initial Balance (IB)
- High/low of first session window (typically 30–60 minutes)
- Defines early equilibrium range

### Breakout Confirmation
- Requires CLOSE outside IB (not wick)
- Directional commitment signal

### Retracement Zone
- 45%–55% of IB range (typical research band)
- Acts as liquidity re-entry zone

### Conviction Filter
- Measures strength of breakout (distance, volume, momentum)

---

## 4. The Trade

### Entry
1. IB forms
2. Price closes outside IB (confirmed breakout)
3. Wait for retracement back into IB
4. Place limit order at retracement zone

### Stop
- Beyond IB opposite side or IB-based buffer

### Target
- Extension beyond breakout direction
- Typically IB range multiple expansion

### Exit
- Time-based expiry if not filled
- Forced exit end of session

---

## 5. Parameters to Research

- IB window duration (30/45/60/90 min)
- Breakout confirmation threshold (close distance beyond IB)
- Retracement entry level (45%–55% band optimisation)
- Stop placement methodology (fixed vs IB-based)
- Target multiples (1R–3R optimisation)
- Minimum IB volatility filter
- Maximum IB size filter
- Breakout conviction scoring features
- Time-to-entry expiry window

---

## 6. AI Research Prompt

> Build a backtesting engine for IB50 using MES/MNQ 5-minute data.
>
> Steps:
> 1. Construct Initial Balance per session
> 2. Detect confirmed breakout (close beyond IB)
> 3. Measure breakout strength using:
>    - Distance beyond IB
>    - Volume spike
>    - ATR context
> 4. Simulate retracement into IB zone (45–55%)
> 5. Execute limit entry and track outcome
>
> Run walk-forward optimisation:
> - Train: 12 months
> - Test: 6 months
>
> Evaluate:
> - Expectancy
> - Fill rate
> - Slippage sensitivity
> - Stability across regimes
>
> Output best parameter set and sensitivity heatmaps.

---

## 7. When It Breaks

- Strong trend days with no retracement
- Low volatility sessions (no meaningful IB expansion)
- News-driven runaway markets
- Overextended pre-market conditions

---

## 8. Typical Performance

Typical observed characteristics:

- Win rate: 40–55%
- Higher average win than loss (asymmetric R:R)
- Missed trades during strong trends (intentional)
- Sensitive to execution quality and fill assumptions

---

## 9. How We Know It Works

Validated through:

- Walk-forward testing across multi-year datasets
- Out-of-sample robustness across MES and MNQ
- Fill simulation vs market order benchmarks
- Sensitivity analysis on retracement band
- Regime segmentation (trend vs mean-reversion environments)