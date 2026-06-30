"""
Live Runner: Poll BarBridge CSV, run strategy, POST signals to OrderRouter.

Two modes:


Local (development): CSV file on disk
Production: Railway backend (coming later)


Usage:
python live_runner.py

Logs:
logs/runner.log — every bar, every signal
"""

import pandas as pd
import time
import os
import requests
import logging
from datetime import datetime

Setup logging

os.makedirs('logs', exist_ok=True)
logging.basicConfig(
level=logging.INFO,
format='%(asctime)s - %(levelname)s - %(message)s',
handlers=[
logging.FileHandler('logs/runner.log'),
logging.StreamHandler()
]
)
logger = logging.getLogger(name)

Import strategy

from strategies.orb import run_orb

def load_bars_from_csv(filepath='data/live/MES_1m.csv'):
"""Load bars from BarBridge CSV."""
if not os.path.exists(filepath):
return None

try:
    df = pd.read_csv(filepath)
    df['time'] = pd.to_datetime(df['time'])
    return df
except:
    return None

def post_signal(action, instrument, quantity=1):
"""POST signal to OrderRouter."""

if action == 'FLAT':
    return  # No action

signal = {
    'action': action,
    'instrument': instrument,
    'quantity': quantity,
    'timestamp': datetime.now().isoformat()
}

try:
    response = requests.post(
        'http://localhost:8765/signal',
        json=signal,
        timeout=2
    )
    
    if response.status_code == 200:
        logger.info(f"Signal posted: {action} {quantity} {instrument}")
    else:
        logger.error(f"Signal post failed: {response.status_code}")

except requests.exceptions.ConnectionError:
    logger.error("Cannot connect to OrderRouter at localhost:8765")
except Exception as e:
    logger.error(f"Signal post error: {e}")

def run_live():
"""Main loop: poll CSV, run strategy, send signals."""

logger.info("Live Runner started")
logger.info("Polling data/live/MES_1m.csv for new bars...")

last_bar_time = None
position = {'side': None}

while True:
    try:
        # Load bars
        df = load_bars_from_csv()
        
        if df is None or df.empty:
            logger.warning("No bars yet. Waiting...")
            time.sleep(1)
            continue
        
        current_bar = df.iloc[-1]
        current_time = current_bar['time']
        
        # Check for new bar
        if last_bar_time == current_time:
            time.sleep(1)
            continue
        
        # New bar
        logger.info(f"Bar: {current_time} OHLCV={current_bar['open']:.0f}/{current_bar['high']:.0f}/{current_bar['low']:.0f}/{current_bar['close']:.0f}/{current_bar['volume']:.0f}")
        
        # Run strategy
        signal = run_orb(df, position)
        
        if signal['action'] != 'FLAT':
            logger.info(f"Signal: {signal['action']} (confidence: {signal['confidence']:.2f})")
            post_signal(signal['action'], 'MES 09-26', quantity=1)
            position['side'] = signal['action']
        
        last_bar_time = current_time
        time.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("Stopping...")
        break
    except Exception as e:
        logger.error(f"Error: {e}")
        time.sleep(5)

if name == 'main':
run_live()
