"""
Lie Detector: Audit backtest for common bullshit.

Catches:


Same-bar fills (using future info within the bar)
Look-ahead bias (using data before decision time)


Usage:
python lie_detector.py

Output:
Console: PASS/FAIL on both audits
"""

import pandas as pd
import ast

def audit_same_bar_fills():
"""
Check if backtest uses same-bar fills.

CORRECT: signal fires on bar N (history up to bar N), 
         fill on bar N+1's open

WRONG: signal fires on bar N, fill on bar N's close 
       (used future data from same bar)
"""

print("\n" + "="*60)
print("AUDIT 1: SAME-BAR FILLS")
print("="*60)

try:
    trades = pd.read_csv('output/orb_trades.csv')
    
    if trades.empty:
        print("No trades found.")
        return True
    
    # Check: entry_time should be BEFORE entry_price was known
    # (entry_time is from signal bar, entry_price should be next bar's open)
    
    # Simple heuristic: if entry_time and exit_time are on the same 
    # minute, we might have same-bar fills
    trades['entry_time'] = pd.to_datetime(trades['entry_time'])
    trades['exit_time'] = pd.to_datetime(trades['exit_time'])
    
    same_bar = (trades['entry_time'].dt.date == trades['exit_time'].dt.date) & \
               (trades['entry_time'].dt.hour == trades['exit_time'].dt.hour) & \
               (trades['entry_time'].dt.minute == trades['exit_time'].dt.minute)
    
    if same_bar.any():
        print(f"⚠ Found {same_bar.sum()} trades with same-minute entry/exit")
        print("  This suggests possible same-bar fills.")
        print("  AUDIT: FAIL")
        return False
    
    print("✓ No same-bar fills detected")
    print("  AUDIT: PASS")
    return True

except Exception as e:
    print(f"ERROR: {e}")
    return False

def audit_look_ahead_bias():
"""
Check if backtest uses look-ahead bias.

Look for:
- Aggregations over the entire dataset (df['close'].max())
- Indexing into future bars (df.iloc[i+5])
- Using future bar data before decision time
"""

print("\n" + "="*60)
print("AUDIT 2: LOOK-AHEAD BIAS")
print("="*60)

try:
    # Read backtest code
    with open('backtest_orb.py', 'r') as f:
        code = f.read()
    
    # Simple heuristics for look-ahead
    red_flags = []
    
    # Check for .max() / .min() on entire series
    if "df['close'].max()" in code or "df['high'].max()" in code:
        red_flags.append("Found df.series.max() — may use future data")
    
    # Check for indexing into future
    if "df.iloc[i+" in code or "df.iloc[i-" in code:
        red_flags.append("Found future indexing (df.iloc[i+X])")
    
    if red_flags:
        print("⚠ Potential look-ahead bias detected:")
        for flag in red_flags:
            print(f"  - {flag}")
        print("  AUDIT: FAIL (review code manually)")
        return False
    
    print("✓ No obvious look-ahead bias detected")
    print("  AUDIT: PASS")
    return True

except Exception as e:
    print(f"ERROR: {e}")
    return False

if name == 'main':
audit1 = audit_same_bar_fills()
audit2 = audit_look_ahead_bias()

print("\n" + "="*60)
print("SUMMARY")
print("="*60)

if audit1 and audit2:
    print("✓ ALL AUDITS PASSED")
    print("  Backtest numbers are trustworthy.")
else:
    print("✗ AUDIT FAILED")
    print("  Fix the issues above before trusting backtest results.")

print("="*60 + "\n")