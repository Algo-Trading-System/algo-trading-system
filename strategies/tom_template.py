# tom_template.py

"""
Turn of Month (TOM) Strategy Template
=====================================

Framework
---------
Turn of Month (TOM) is a calendar-based strategy that exploits the
historically observed tendency for equity markets to outperform around
the transition between calendar months.

Unlike the other strategies in the stack, TOM is NOT reactive to price.
It is anticipatory: the calendar determines whether a trade is taken.

Markets
-------
- MES (Micro E-mini S&P 500)
- MNQ (Micro E-mini Nasdaq-100)
- MGC (Micro Gold)

Timeframe
---------
Intraday execution (typically enter at the RTH open and exit by the
RTH close).

Concept
-------
Institutional capital flows often cluster around month-end and the
beginning of a new month due to:

- Pension contributions
- Retirement account inflows
- Mutual fund rebalancing
- Index adjustments
- Institutional allocation changes

Research has shown that these flows can create a positive return bias
around specific trading days of each month.

Each instrument has its own validated trading-day calendar. The exact
day ranks and inclusion rules are proprietary.

Trade Flow
----------
1. Determine today's trading-day rank within the month.
2. Look up whether today is an eligible TOM day for the instrument.
3. At the RTH open (09:30 ET), submit a LONG market order.
4. Attach a fixed hard stop.
5. Hold until:
    - Stop is hit, or
    - Forced exit at 16:00 ET.
6. Only one trade per instrument per day.

This strategy is long-only.

No breakout logic, no mean reversion, no price levels, and no machine
learning model are involved.

Research Areas
--------------
- Trading-day rank definitions
- Instrument-specific TOM windows
- Inclusion of last trading day of prior month
- Hard stop size
- Position sizing
- Session definition
- Holiday adjustments
- Volatility filters
- Instrument selection

Validation
----------
Research should include:

- Multi-year walk-forward testing
- Out-of-sample validation
- Slippage and commission modelling
- Stability across market regimes
- Comparison against buy-and-hold and random-entry baselines

"""

from __future__ import annotations

import pandas as pd


def run_tom(
    df: pd.DataFrame,
    position_state: dict,
) -> dict:
    """
    Execute Turn of Month strategy.

    Parameters
    ----------
    df
        OHLCV dataframe.

    position_state
        Current live position state.

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
    Determine today's instrument.

    STEP 2
    -------
    Load instrument-specific TOM calendar.

    Examples:

        MES
        MNQ
        MGC

    Each may use different valid day-ranks.

    STEP 3
    -------
    Calculate today's trading-day rank.

    Examples:

        First trading day
        Second trading day
        Last trading day
        etc.

    STEP 4
    -------
    If today is NOT a valid TOM day:

        return FLAT

    STEP 5
    -------
    Wait until 09:30 ET RTH open.

    STEP 6
    -------
    Submit LONG market order.

    Attach:

        • Hard stop
        • Forced end-of-day exit

    STEP 7
    -------
    Prevent duplicate entries.

    One trade per instrument per day.

    STEP 8
    -------
    Force flat at 16:00 ET regardless of PnL.

    """

    # -------------------------------------------------
    # TODO
    # Determine trading-day rank
    # -------------------------------------------------

    # -------------------------------------------------
    # TODO
    # Load instrument calendar
    # -------------------------------------------------

    # -------------------------------------------------
    # TODO
    # Validate TOM day
    # -------------------------------------------------

    # -------------------------------------------------
    # TODO
    # Wait for RTH open
    # -------------------------------------------------

    # -------------------------------------------------
    # TODO
    # Submit long market order
    # -------------------------------------------------

    # -------------------------------------------------
    # TODO
    # Attach hard stop
    # -------------------------------------------------

    # -------------------------------------------------
    # TODO
    # Force end-of-day exit
    # -------------------------------------------------

    return {
        "action": "FLAT",
        "confidence": 0.0,
    }
