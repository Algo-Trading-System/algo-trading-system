"""
Opening Range Breakout (ORB) Backtest Harness

Load historical 1-minute bars, run ORB strategy, measure P&L.
This is intentionally unprofitable — it's scaffolding to prove the rails work.

Usage:
    python backtest_orb.py

Output:
    output/orb_trades.csv — all trades
    Console: summary stats (win rate, PF, max DD, Sharpe)
"""

import pandas as pd
import numpy as np
from datetime import datetime, time
import os

# Load data
def load_data(filepath='data/MES_1m.parquet'):
    """Load 1-minute bars from parquet."""
    if not os.path.exists(filepath):
        print(f"ERROR: {filepath} not found. Run download_data.py first.")
        return None
    df = pd.read_parquet(filepath)
    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values('time').reset_index(drop=True)
    return df

# ORB Strategy Logic
def run_orb(bar_history, current_position):
    """
    ORB strategy: fade the opening range breakout.
    
    Input: DataFrame of bars up to current bar, dict of position state
    Output: dict with action (LONG/SHORT/FLAT), confidence (0-1)
    
    Logic:
    - Opening range: first 30 min of day (9:30-10:00 ET)
    - High/Low of that 30 min = OR range
    - After 10:00 ET: if price breaks above OR high or below OR low, fade it
    - Entry: next bar's open after break signal
    - Stop: 5 points
    - Target: 10 points
    - Exit: 3:55 PM ET or stop/target hit
    """
    
    if bar_history.empty:
        return {'action': 'FLAT', 'confidence': 0}
    
    current_bar = bar_history.iloc[-1]
    current_time = current_bar['time']
    current_hour = current_time.hour
    current_minute = current_time.minute
    
    # Extract date
    current_date = current_time.date()
    
    # Filter bars for today (same date)
    today_bars = bar_history[bar_history['time'].dt.date == current_date].copy()
    
    if len(today_bars) < 2:
        return {'action': 'FLAT', 'confidence': 0}
    
    # Opening range: 9:30-10:00 ET (first 30 min)
    market_open = time(9, 30)
    or_end = time(10, 0)
    
    or_bars = today_bars[
        (today_bars['time'].dt.time >= market_open) & 
        (today_bars['time'].dt.time < or_end)
    ]
    
    if len(or_bars) == 0:
        return {'action': 'FLAT', 'confidence': 0}
    
    or_high = or_bars['high'].max()
    or_low = or_bars['low'].min()
    
    # After 10:00 ET, before 3:55 PM
    if not (current_time.time() >= or_end and current_time.time() < time(15, 55)):
        return {'action': 'FLAT', 'confidence': 0}
    
    # Check for breakout
    close = current_bar['close']
    
    if close > or_high:
        # Broke above OR high — FADE (short)
        return {'action': 'SHORT', 'confidence': 0.5}
    elif close < or_low:
        # Broke below OR low — FADE (long)
        return {'action': 'LONG', 'confidence': 0.5}
    
    return {'action': 'FLAT', 'confidence': 0}

# Backtest
def backtest_orb(df):
    """Run backtest on historical data."""
    
    trades = []
    position = {'side': None, 'entry_price': None, 'entry_time': None}
    
    for i in range(1, len(df)):
        current_bar = df.iloc[i]
        history = df.iloc[:i+1]
        
        # Skip if not a trading hour (9:30 AM - 3:55 PM ET)
        current_time = current_bar['time']
        if current_time.hour < 9 or (current_time.hour >= 16):
            continue
        
        # Get signal
        signal = run_orb(history, position)
        
        # Exit at 3:55 PM
        if current_time.time() >= time(15, 55) and position['side']:
            exit_price = current_bar['open']  # Next bar's open
            pnl = (exit_price - position['entry_price']) * (1 if position['side'] == 'LONG' else -1)
            pnl -= 0.62  # Commission: $0.62 round-turn
            pnl -= abs(exit_price - position['entry_price']) * 0.0625  # Slippage: 1 tick = 0.0625
            
            trades.append({
                'entry_time': position['entry_time'],
                'exit_time': current_time,
                'side': position['side'],
                'entry_price': position['entry_price'],
                'exit_price': exit_price,
                'pnl': pnl
            })
            position = {'side': None, 'entry_price': None, 'entry_time': None}
        
        # Enter new position
        if signal['action'] != 'FLAT' and not position['side']:
            position['side'] = signal['action']
            position['entry_price'] = current_bar['open']
            position['entry_time'] = current_time
        
        # Stop/Target exits
        if position['side']:
            if position['side'] == 'LONG':
                stop_price = position['entry_price'] - 5
                target_price = position['entry_price'] + 10
                
                if current_bar['low'] <= stop_price:
                    exit_price = stop_price
                    pnl = (exit_price - position['entry_price']) - 0.62
                    trades.append({
                        'entry_time': position['entry_time'],
                        'exit_time': current_time,
                        'side': 'LONG',
                        'entry_price': position['entry_price'],
                        'exit_price': exit_price,
                        'pnl': pnl
                    })
                    position = {'side': None, 'entry_price': None, 'entry_time': None}
                
                elif current_bar['high'] >= target_price:
                    exit_price = target_price
                    pnl = (exit_price - position['entry_price']) - 0.62
                    trades.append({
                        'entry_time': position['entry_time'],
                        'exit_time': current_time,
                        'side': 'LONG',
                        'entry_price': position['entry_price'],
                        'exit_price': exit_price,
                        'pnl': pnl
                    })
                    position = {'side': None, 'entry_price': None, 'entry_time': None}
            
            else:  # SHORT
                stop_price = position['entry_price'] + 5
                target_price = position['entry_price'] - 10
                
                if current_bar['high'] >= stop_price:
                    exit_price = stop_price
                    pnl = (position['entry_price'] - exit_price) - 0.62
                    trades.append({
                        'entry_time': position['entry_time'],
                        'exit_time': current_time,
                        'side': 'SHORT',
                        'entry_price': position['entry_price'],
                        'exit_price': exit_price,
                        'pnl': pnl
                    })
                    position = {'side': None, 'entry_price': None, 'entry_time': None}
                
                elif current_bar['low'] <= target_price:
                    exit_price = target_price
                    pnl = (position['entry_price'] - exit_price) - 0.62
                    trades.append({
                        'entry_time': position['entry_time'],
                        'exit_time': current_time,
                        'side': 'SHORT',
                        'entry_price': position['entry_price'],
                        'exit_price': exit_price,
                        'pnl': pnl
                    })
                    position = {'side': None, 'entry_price': None, 'entry_time': None}
    
    return pd.DataFrame(trades)

# Summary stats
def print_stats(trades_df):
    """Print backtest summary statistics."""
    
    if trades_df.empty:
        print("No trades generated.")
        return
    
    total_trades = len(trades_df)
    winners = (trades_df['pnl'] > 0).sum()
    losers = (trades_df['pnl'] < 0).sum()
    win_rate = (winners / total_trades * 100) if total_trades > 0 else 0
    
    gross_profit = trades_df[trades_df['pnl'] > 0]['pnl'].sum()
    gross_loss = abs(trades_df[trades_df['pnl'] < 0]['pnl'].sum())
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
    
    total_pnl = trades_df['pnl'].sum()
    max_dd = trades_df['pnl'].cumsum().min()
    
    expectancy = total_pnl / total_trades if total_trades > 0 else 0
    
    returns = trades_df['pnl'].values
    sharpe = np.mean(returns) / (np.std(returns) + 1e-6) * np.sqrt(252 * 6.5) if len(returns) > 1 else 0
    
    print("\n" + "="*60)
    print("ORB BACKTEST RESULTS")
    print("="*60)
    print(f"Total Trades:        {total_trades}")
    print(f"Winners:             {winners}")
    print(f"Losers:              {losers}")
    print(f"Win Rate:            {win_rate:.1f}%")
    print(f"Gross Profit:        ${gross_profit:.0f}")
    print(f"Gross Loss:          ${gross_loss:.0f}")
    print(f"Profit Factor:       {profit_factor:.2f}")
    print(f"Total P&L:           ${total_pnl:.0f}")
    print(f"Max Drawdown:        ${max_dd:.0f}")
    print(f"Expectancy:          ${expectancy:.0f} per trade")
    print(f"Sharpe Ratio:        {sharpe:.2f}")
    print("="*60 + "\n")

# Main
if __name__ == '__main__':
    print("Loading data...")
    df = load_data()
    
    if df is not None:
        print(f"Loaded {len(df)} bars from {df['time'].min()} to {df['time'].max()}")
        
        print("Running backtest...")
        trades = backtest_orb(df)
        
        # Save trades
        os.makedirs('output', exist_ok=True)
        trades.to_csv('output/orb_trades.csv', index=False)
        print(f"Saved {len(trades)} trades to output/orb_trades.csv")
        
        # Print stats
        print_stats(trades)
        