"""
Download 1-minute OHLCV bars from Databento.

Usage:
python download_data.py

Output:
data/MES_1m.parquet — 5 years of 1-minute bars for MES
"""

import os
import databento as db
import pandas as pd
from datetime import datetime, timedelta

def download_mes_data():
"""Download MES 1-minute bars from 2021-01-01 to today."""

api_key = os.getenv('DATABENTO_API_KEY')
if not api_key:
    print("ERROR: DATABENTO_API_KEY not set in .env")
    return False

client = db.Historical(api_key=api_key)

print("Downloading MES 1-minute bars from 2021-01-01 to today...")

try:
    # Fetch data
    data = client.timeseries(
        dataset="GLBX.MDP3",
        symbols=["MES.n.0"],  # MES continuous contract
        schema="ohlcv",
        start="2021-01-01",
        end=datetime.now().strftime("%Y-%m-%d"),
        bar_size=60,  # 1 minute
    )
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Rename columns to match our format
    df = df.rename(columns={
        'ts_event': 'time',
        'open': 'open',
        'high': 'high',
        'low': 'low',
        'close': 'close',
        'volume': 'volume'
    })
    
    # Convert timestamp to datetime
    df['time'] = pd.to_datetime(df['ts_event'], unit='ns')
    df = df[['time', 'open', 'high', 'low', 'close', 'volume']]
    
    # Save to parquet
    os.makedirs('data', exist_ok=True)
    df.to_parquet('data/MES_1m.parquet', index=False)
    
    print(f"✓ Downloaded {len(df)} bars")
    print(f"  Date range: {df['time'].min()} to {df['time'].max()}")
    print(f"  Saved to data/MES_1m.parquet")
    
    return True

except Exception as e:
    print(f"ERROR: {e}")
    return False

if name == 'main':
download_mes_data()