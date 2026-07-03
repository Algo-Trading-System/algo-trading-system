# orb.py
"""
Educational Opening Range Breakout (ORB) Strategy

This is a complete reference implementation of a simple Opening Range
Breakout mean-reversion strategy.

Strategy
--------
- Instrument agnostic
- 5-minute bars
- Opening Range = 09:30–10:00 ET
- After 10:00 ET:
    * First close ABOVE OR high -> SHORT (fade)
    * First close BELOW OR low  -> LONG (fade)
- Entry occurs on next bar open
- Stop = 5 points
- Target = 10 points
- Force exit = 15:55 ET

Expected DataFrame columns
--------------------------
timestamp (datetime64)
open
high
low
close
volume

Return
------
{
    "action": "LONG" | "SHORT" | "FLAT",
    "confidence": float
}
"""

from __future__ import annotations

import pandas as pd
from datetime import time


OPENING_START = time(9, 30)
OPENING_END = time(10, 0)
FORCE_EXIT = time(15, 55)

STOP_POINTS = 5.0
TARGET_POINTS = 10.0


def _ensure_timestamp(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure timestamp column exists as datetime."""

    if "timestamp" not in df.columns:
        raise ValueError("DataFrame must contain 'timestamp' column")

    if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
        df = df.copy()
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df


def _opening_range(df: pd.DataFrame):
    """Calculate opening range."""

    session = df[
        (df["timestamp"].dt.time >= OPENING_START)
        & (df["timestamp"].dt.time < OPENING_END)
    ]

    if session.empty:
        return None, None

    return (
        session["high"].max(),
        session["low"].min(),
    )


def run_orb(
    df: pd.DataFrame,
    position_state: dict,
) -> dict:
    """
    Execute ORB strategy.

    Parameters
    ----------
    df
        Intraday OHLCV bars.

    position_state
        Dictionary describing current live position.

        Example

        {
            "side": None,
            "entry": None,
            "stop": None,
            "target": None
        }

    Returns
    -------
    dict
    """

    df = _ensure_timestamp(df)

    if len(df) < 10:
        return {
            "action": "FLAT",
            "confidence": 0.0,
        }

    orb_high, orb_low = _opening_range(df)

    if orb_high is None:
        return {
            "action": "FLAT",
            "confidence": 0.0,
        }

    latest = df.iloc[-1]
    now = latest["timestamp"].time()

    # -------------------------------------
    # Manage existing position
    # -------------------------------------

    if position_state.get("side") == "LONG":

        if latest["low"] <= position_state["stop"]:
            return {
                "action": "FLAT",
                "confidence": 1.0,
            }

        if latest["high"] >= position_state["target"]:
            return {
                "action": "FLAT",
                "confidence": 1.0,
            }

        if now >= FORCE_EXIT:
            return {
                "action": "FLAT",
                "confidence": 1.0,
            }

        return {
            "action": "LONG",
            "confidence": 1.0,
        }

    if position_state.get("side") == "SHORT":

        if latest["high"] >= position_state["stop"]:
            return {
                "action": "FLAT",
                "confidence": 1.0,
            }

        if latest["low"] <= position_state["target"]:
            return {
                "action": "FLAT",
                "confidence": 1.0,
            }

        if now >= FORCE_EXIT:
            return {
                "action": "FLAT",
                "confidence": 1.0,
            }

        return {
            "action": "SHORT",
            "confidence": 1.0,
        }

    # -------------------------------------
    # No entries before OR complete
    # -------------------------------------

    if now < OPENING_END:
        return {
            "action": "FLAT",
            "confidence": 0.0,
        }

    # -------------------------------------
    # Find first breakout AFTER 10:00
    # -------------------------------------

    post_or = df[df["timestamp"].dt.time >= OPENING_END]

    if post_or.empty:
        return {
            "action": "FLAT",
            "confidence": 0.0,
        }

    signal = None

    for _, row in post_or.iterrows():

        if row["close"] > orb_high:
            signal = "SHORT"
            break

        if row["close"] < orb_low:
            signal = "LONG"
            break

    if signal is None:
        return {
            "action": "FLAT",
            "confidence": 0.0,
        }

    # -------------------------------------
    # Next-bar entry
    # -------------------------------------

    signal_index = post_or.index.get_loc(row.name)

    if signal_index + 1 >= len(post_or):
        return {
            "action": "FLAT",
            "confidence": 0.0,
        }

    entry_bar = post_or.iloc[signal_index + 1]

    entry = float(entry_bar["open"])

    if signal == "LONG":

        stop = entry - STOP_POINTS
        target = entry + TARGET_POINTS

        position_state.update(
            {
                "side": "LONG",
                "entry": entry,
                "stop": stop,
                "target": target,
            }
        )

        return {
            "action": "LONG",
            "confidence": 0.82,
        }

    stop = entry + STOP_POINTS
    target = entry - TARGET_POINTS

    position_state.update(
        {
            "side": "SHORT",
            "entry": entry,
            "stop": stop,
            "target": target,
        }
    )

    return {
        "action": "SHORT",
        "confidence": 0.82,
    }
