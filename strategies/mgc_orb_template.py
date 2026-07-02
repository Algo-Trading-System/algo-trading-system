# mgc_orb_template.py

"""
MGC ORB Strategy Template
=========================

Framework
---------
MGC ORB is a time-of-day Opening Range Breakout strategy designed for
Micro Gold (MGC). Unlike a traditional session-based ORB, this framework
builds two independent opening ranges each trading day around canonical
U.S. macroeconomic release times.

Markets
-------
- MGC (Micro Gold Futures)

Timeframe
---------
5-minute bars

Trading Windows
---------------
Two independent daily windows:

- 08:30 ET
- 10:00 ET

These windows are ALWAYS evaluated on weekdays regardless of whether
economic data is actually released. The edge comes from the recurring
liquidity profile around these times rather than explicit calendar
gating.

Concept
-------
The strategy constructs an Opening Range (OR) from the first N bars
following each configured window start.

Once the OR is complete:

1. Monitor for a confirmed CLOSE outside the OR.
2. Trigger a directional breakout signal.
3. Entry is ANCHORED to the OR boundary (retracement entry),
   not the breakout candle's close.
4. Attach asymmetric risk/reward brackets.
5. Close all positions before the NY cash close.

Unlike a classic ORB that enters immediately on breakout, this framework
expects a pullback to the OR boundary before entry.

Key Framework Components
------------------------
• Two independent daily OR windows
• Opening Range construction
• Time-of-day scheduler
• Range sanity filter
• Range size cap
• Directional filters
• Bar-close breakout confirmation
• Anchored retracement entries
• One trade per window
• Forced end-of-day exit

State Machine
-------------
Each window progresses independently through:

    pre_news
        ↓
    building_orb
        ↓
    armed
        ↓
    done

State is reset daily.

A restart should restore state from persistent storage so that signals
are never duplicated after an engine restart.

Research Areas
--------------
Human research should determine:

- Number of OR bars
- Window duration
- Holding period
- Minimum OR size
- Maximum OR size cap
- Long-side filters
- Weekday filters
- Entry confirmation
- Entry anchoring rules
- Stop multiple
- Target multiple
- Risk sizing
- Position sizing
- Volatility filters

Validation
----------
Recommended research pipeline:

- Walk-forward optimisation
- Out-of-sample validation
- Slippage modelling
- Live shadow testing
- Stability analysis
- Regime analysis

"""

from __future__ import annotations

import pandas as pd


def run_mgc_orb(
    df: pd.DataFrame,
    position_state: dict,
) -> dict:
    """
    Execute MGC ORB strategy.

    Parameters
    ----------
    df
        Five-minute OHLCV bars.

    position_state
        Current strategy state and open position information.

    Returns
    -------
    dict

    {
        "action": "LONG" | "SHORT" | "FLAT",
        "confidence": float
    }

    TODO IMPLEMENTATION
    -------------------

    STEP 1
    -------
    Determine active trading window.

        • 08:30 ET
        • 10:00 ET

    Maintain completely independent state for both.

    STEP 2
    -------
    Build Opening Range.

    Record:

        • OR High
        • OR Low
        • Range Size

    STEP 3
    -------
    Validate OR size.

        • Skip tiny ranges
        • Cap oversized ranges

    STEP 4
    -------
    Wait for CLOSE beyond OR.

    Ignore wick-only breaks.

    STEP 5
    -------
    Apply directional filter.

    Research examples:

        • Long disabled in selected windows
        • Weekday-specific filters
        • Volatility regime filters

    STEP 6
    -------
    Create anchored entry.

    IMPORTANT:

    Entry is NOT the breakout close.

    Entry is placed at the broken OR boundary
    and waits for a retracement fill.

    STEP 7
    -------
    Attach stop and target.

    Research:

        • Range-based stop
        • Range multiple target
        • Asymmetric reward:risk

    STEP 8
    -------
    Expire trade if:

        • Holding window ends
        • Window expires
        • Session ends

    STEP 9
    -------
    Force flat before NY cash close.

    STEP 10
    --------
    Persist state.

    Store:

        • Current window
        • OR values
        • Armed status
        • Entry submitted
        • Filled status
        • Position state

    Ensure engine restart never duplicates a signal.

    """

    # --------------------------------------------------
    # TODO
    # Determine active OR window
    # --------------------------------------------------

    # --------------------------------------------------
    # TODO
    # Build Opening Range
    # --------------------------------------------------

    # --------------------------------------------------
    # TODO
    # Validate OR size
    # --------------------------------------------------

    # --------------------------------------------------
    # TODO
    # Detect breakout close
    # --------------------------------------------------

    # --------------------------------------------------
    # TODO
    # Apply directional filters
    # --------------------------------------------------

    # --------------------------------------------------
    # TODO
    # Submit anchored retracement entry
    # --------------------------------------------------

    # --------------------------------------------------
    # TODO
    # Attach bracket orders
    # --------------------------------------------------

    # --------------------------------------------------
    # TODO
    # Maintain state machine
    # --------------------------------------------------

    # --------------------------------------------------
    # TODO
    # Force end-of-day cleanup
    # --------------------------------------------------

    return {
        "action": "FLAT",
        "confidence": 0.0,
    }