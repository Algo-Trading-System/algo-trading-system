# MGC ORB Framework

## 1. Framework Name & Concept

MGC ORB is a time-of-day Opening Range Breakout strategy applied to Micro Gold (MGC). It builds short intraday opening ranges around two fixed U.S. macro-liquidity windows and trades the directional expansion that follows failed acceptance of those ranges.

Unlike standard ORB systems, it is explicitly time-scheduled rather than session-based and uses anchored retracement entries rather than immediate breakout execution.

---

## 2. Why It Works

The edge is driven by structural liquidity behaviour in gold:

- USD macro data releases concentrate volatility into predictable windows
- Market makers widen spreads and reposition inventory pre-release
- Order flow imbalance increases around 08:30 and 10:00 ET
- Gold reacts asymmetrically to USD repricing events

The inefficiency is not prediction of news, but *consistent liquidity clustering at fixed times*, regardless of whether data prints.

---

## 3. Key Concepts

### Time-of-Day Windows
- 08:30 ET (primary macro release cluster)
- 10:00 ET (secondary macro release cluster)

### Opening Range (OR)
- First N bars after window start
- Defines short-term equilibrium

### Breakout Confirmation
- Requires CLOSE beyond OR boundary
- Wick-only breaks are ignored

### Anchored Entry
- Entry is placed at OR boundary
- Requires retracement after breakout confirmation

### State Machine
- pre_news → building_orb → armed → done
- Each window operates independently

---

## 4. The Trade

### Entry Flow
1. OR forms after window open
2. Price closes outside OR (breakout confirmation)
3. Signal arms
4. Entry placed at OR boundary
5. Wait for retracement fill

### Stop
- Opposite side of OR or capped risk multiple

### Target
- Asymmetric expansion beyond OR range (typically >1R)

### Exit Rules
- Forced exit by NY close
- Window expiry exit
- Time-based invalidation

### Constraints
- One trade per window per day
- Independent logic per time window
- No overnight holding

---

## 5. Parameters to Research

- OR duration (5/10/15/30 min)
- Window selection (08:30 vs 10:00 weighting)
- Minimum OR size filter
- Maximum OR size cap
- Directional bias rules (long/short asymmetry)
- Entry confirmation threshold (close distance beyond OR)
- Retracement fill tolerance
- Stop/target multiples
- Volatility regime filters
- Session expiry timing

---

## 6. AI Research Prompt

> Build a backtesting engine for MGC ORB using 5-minute gold futures data.
>
> Requirements:
> 1. Construct opening ranges at 08:30 and 10:00 ET daily
> 2. Detect breakout only on CLOSE beyond range
> 3. Simulate anchored entry at OR boundary after breakout confirmation
> 4. Model retracement-based fills (missed trades allowed)
>
> Include:
> - OR window length optimization
> - Directional filter testing
> - Volatility regime segmentation
>
> Evaluation:
> - Expectancy per window
> - Fill rate sensitivity
> - Sharpe contribution vs other strategies
> - Drawdown clustering analysis
>
> Use walk-forward validation (12-month train / 6-month test).

---

## 7. When It Breaks

- Strong trend days with no retracement
- News shock continuation without pullback
- Extremely low volatility regimes (insufficient OR structure)
- Structural changes in USD macro reaction function

---

## 8. Typical Performance

Observed characteristics:

- Moderate win rate (~45–55% depending on window)
- Asymmetric payoff distribution (winners larger than losers)
- Missed trades during strong trend expansion (expected behaviour)
- Sensitivity to execution quality (fill assumptions matter)

---

## 9. How We Know It Works

Validated via:

- Multi-year intraday walk-forward testing on MGC
- Out-of-sample robustness checks across volatility regimes
- Fill simulation vs idealised execution models
- Stability analysis across OR parameter sweeps
- Cross-validation against MES/MNQ ORB structures
