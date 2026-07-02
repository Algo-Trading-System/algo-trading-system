-- Supabase Schema for Trading System
-- Tracks bars, signals, fills, trades, and account state

-- Bars table: Every 1-minute bar
CREATE TABLE bars (
    id BIGSERIAL PRIMARY KEY,
    instrument TEXT NOT NULL,
    time TIMESTAMP NOT NULL,
    open NUMERIC(10, 2),
    high NUMERIC(10, 2),
    low NUMERIC(10, 2),
    close NUMERIC(10, 2),
    volume BIGINT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_bars_time ON bars(time);
CREATE INDEX idx_bars_instrument ON bars(instrument);

-- Signals table: Every signal fired by strategy
CREATE TABLE signals (
    id BIGSERIAL PRIMARY KEY,
    strategy TEXT NOT NULL,
    time TIMESTAMP NOT NULL,
    action TEXT NOT NULL, -- LONG, SHORT, FLAT
    confidence NUMERIC(3, 2),
    instrument TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_signals_time ON signals(time);
CREATE INDEX idx_signals_strategy ON signals(strategy);

-- Fills table: Every order execution
CREATE TABLE fills (
    id BIGSERIAL PRIMARY KEY,
    order_id TEXT UNIQUE,
    account TEXT,
    strategy TEXT,
    instrument TEXT,
    side TEXT NOT NULL, -- LONG, SHORT
    quantity INT,
    price NUMERIC(10, 2),
    time TIMESTAMP NOT NULL,
    slippage NUMERIC(10, 4),
    commission NUMERIC(10, 2),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_fills_time ON fills(time);
CREATE INDEX idx_fills_account ON fills(account);
CREATE INDEX idx_fills_strategy ON fills(strategy);

-- Trades table: Closed trades (entry + exit)
CREATE TABLE trades (
    id BIGSERIAL PRIMARY KEY,
    account TEXT,
    strategy TEXT,
    entry_time TIMESTAMP NOT NULL,
    exit_time TIMESTAMP NOT NULL,
    side TEXT NOT NULL, -- LONG, SHORT
    entry_price NUMERIC(10, 2),
    exit_price NUMERIC(10, 2),
    quantity INT,
    pnl NUMERIC(10, 2),
    r_multiple NUMERIC(10, 2),
    duration_minutes INT,
    bars_held INT,
    mfe NUMERIC(10, 2), -- Max Favorable Excursion
    mae NUMERIC(10, 2), -- Max Adverse Excursion
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_trades_account ON trades(account);
CREATE INDEX idx_trades_strategy ON trades(strategy);
CREATE INDEX idx_trades_entry_time ON trades(entry_time);

-- Account snapshots: Daily account state
CREATE TABLE account_snapshots (
    id BIGSERIAL PRIMARY KEY,
    account TEXT,
    date DATE,
    opening_balance NUMERIC(12, 2),
    closing_balance NUMERIC(12, 2),
    daily_pnl NUMERIC(12, 2),
    max_intraday_dd NUMERIC(12, 2),
    max_dd_pct NUMERIC(5, 2),
    trades_count INT,
    win_rate NUMERIC(5, 2),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_snapshots_account ON account_snapshots(account);
CREATE INDEX idx_snapshots_date ON account_snapshots(date);

-- Positions table: Current open positions
CREATE TABLE positions (
    id BIGSERIAL PRIMARY KEY,
    account TEXT,
    strategy TEXT,
    instrument TEXT,
    side TEXT, -- LONG, SHORT, or NULL
    quantity INT,
    entry_price NUMERIC(10, 2),
    entry_time TIMESTAMP,
    current_price NUMERIC(10, 2),
    unrealized_pnl NUMERIC(10, 2),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_positions_account ON positions(account);
CREATE INDEX idx_positions_strategy ON positions(strategy);

-- System health table: Monitor downtime, errors
CREATE TABLE system_health (
    id BIGSERIAL PRIMARY KEY,
    component TEXT NOT NULL, -- runner, orderrouter, bridge, supabase
    status TEXT, -- online, offline, error
    last_heartbeat TIMESTAMP,
    error_message TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_health_component ON system_health(component);

-- Alert log: Track all alerts sent
CREATE TABLE alerts (
    id BIGSERIAL PRIMARY KEY,
    alert_type TEXT NOT NULL, -- trade, error, drawdown, health
    message TEXT,
    severity TEXT, -- info, warning, critical
    sent_at TIMESTAMP DEFAULT NOW(),
    read BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_alerts_sent_at ON alerts(sent_at);
CREATE INDEX idx_alerts_read ON alerts(read);
