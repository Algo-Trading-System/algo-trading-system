# Supabase Setup — Database for Production

Supabase is hosted Postgres. Once your system passes paper-trading, you'll log trades to Supabase for monitoring and compliance.

## Step 1: Create Supabase project

1. Go to https://supabase.com
2. Sign up (free tier is fine to start)
3. Click "New Project"
4. Name: "algo-trading-system"
5. Password: strong password (save it)
6. Region: **US East** (closest to CME / Chicago)
7. Wait for project to deploy (~2 min)

## Step 2: Load the schema

Once project is ready:

1. Open your project
2. Left sidebar → SQL Editor → New Query
3. Copy entire contents of `/infra/supabase_schema.sql`
4. Paste into SQL editor
5. Click "Run"
6. Wait for tables to create

Verify: Left sidebar → Tables. You should see:
- bars
- signals
- fills
- trades
- account_snapshots
- positions
- system_health
- alerts

## Step 3: Get your credentials

In Supabase project:

1. Settings → API
2. Copy: **Project URL** (looks like `https://xxxxx.supabase.co`)
3. Copy: **anon public key** (long string)

Add to `.env`:
```
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your_anon_key_here
```

## Step 4: Update live_runner to log to Supabase

In `bridge/live_runner.py`, add at the top:

```python
from supabase import create_client, Client

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None
```

Then when a trade closes:
```python
if supabase:
    supabase.table('trades').insert({
        'account': 'Tradeify',
        'strategy': 'ORB',
        'entry_time': entry_time.isoformat(),
        'exit_time': exit_time.isoformat(),
        'side': side,
        'entry_price': entry_price,
        'exit_price': exit_price,
        'quantity': quantity,
        'pnl': pnl
    }).execute()
```

## Step 5: Set up ASM dashboard to query Supabase

Once trades are logged, update `monitoring/asm_dashboard.py` to read from Supabase:

```python
from supabase import create_client

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_trades():
    response = supabase.table('trades').select('*').order('entry_time', desc=True).limit(50).execute()
    return response.data
```

## Security considerations

**Anon key is public.** It only has read/write access to your tables (via Row Level Security). 

To restrict access:
1. Left sidebar → Authentication → Users
2. Create new user for your IP only (if paranoid)

For live production, you might want:
- **Read-only key** for ASM dashboard
- **Write-only key** for live_runner
- Enable Row Level Security on tables

But for now, the anon key with basic schema is fine.

## Tables quick reference

| Table | Purpose |
|-------|---------|
| **bars** | Store every 1-min bar (optional, for backtesting later) |
| **signals** | Every signal fired by strategy |
| **fills** | Every order execution |
| **trades** | Closed trades (entry + exit) |
| **account_snapshots** | Daily account state (balance, DD, PnL) |
| **positions** | Current open positions (real-time) |
| **system_health** | Monitor runner/router uptime |
| **alerts** | Alert log (errors, trades, drawdowns) |

Most important for you: **trades** and **account_snapshots**.

## Monitoring queries

Log into Supabase SQL Editor to check data:

**Daily P&L:**
```sql
SELECT 
  date(entry_time) as day,
  account,
  count(*) as trades,
  sum(pnl) as daily_pnl,
  avg(pnl) as avg_pnl
FROM trades
GROUP BY date(entry_time), account
ORDER BY day DESC;
```

**Win rate by strategy:**
```sql
SELECT 
  strategy,
  count(*) as total_trades,
  count(CASE WHEN pnl > 0 THEN 1 END) as winners,
  round(100.0 * count(CASE WHEN pnl > 0 THEN 1 END) / count(*), 1) as win_rate_pct
FROM trades
GROUP BY strategy;
```

**Max drawdown (running cumsum):**
```sql
SELECT 
  sum(pnl) as cumulative_pnl,
  min(sum(pnl) OVER (ORDER BY entry_time)) as max_drawdown
FROM trades
WHERE account = 'Tradeify'
ORDER BY entry_time DESC
LIMIT 1;
```

## Cost

- Supabase free tier: **free** (1 GB storage, plenty for trade logs)
- Paid tier if you scale: ~$25/mo for more storage

For most traders, free tier never fills up.

## Next steps

1. Create Supabase project
2. Load schema
3. Test connection from your local machine:
```python
import os
from supabase import create_client

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
result = supabase.table('trades').select('*').limit(1).execute()
print(result.data)  # Should return empty list (no trades yet)
```

4. Once verified, integrate logging into live_runner
5. Deploy to production

Done.
