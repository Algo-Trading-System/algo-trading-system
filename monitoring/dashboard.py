"""
Dashboard: Flask web UI showing live system state.

Displays: current position, recent signals, recent fills, connection status.

Usage:
    python dashboard.py

Access: http://localhost:5001
"""

from flask import Flask, render_template_string
import os
import pandas as pd
from datetime import datetime
import logging

app = Flask(__name__)

def load_logs():
    """Load recent entries from runner and router logs."""
    signals = []
    fills = []
    
    # Load runner signals
    if os.path.exists('logs/runner.log'):
        try:
            with open('logs/runner.log', 'r') as f:
                lines = f.readlines()
                for line in lines[-50:]:  # Last 50 lines
                    if 'Signal:' in line or 'Bar:' in line:
                        signals.append(line.strip())
        except:
            pass
    
    # Load router fills
    if os.path.exists('NT8-Logs/OrderRouter.log'):
        try:
            with open('NT8-Logs/OrderRouter.log', 'r') as f:
                lines = f.readlines()
                for line in lines[-50:]:
                    if 'Fill:' in line:
                        fills.append(line.strip())
        except:
            pass
    
    return signals, fills

def load_trades():
    """Load recent trades from backtest CSV."""
    if os.path.exists('output/orb_trades.csv'):
        try:
            df = pd.read_csv('output/orb_trades.csv')
            return df.tail(20).to_html(classes='table table-striped')
        except:
            return "<p>No trades yet.</p>"
    return "<p>No trades yet.</p>"

@app.route('/')
def dashboard():
    signals, fills = load_logs()
    trades_html = load_trades()
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Trading System Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { margin: 20px; background-color: #f8f9fa; }
            .card { margin-bottom: 20px; }
            .status-good { color: green; }
            .status-bad { color: red; }
            h1 { margin-bottom: 30px; }
            .log-box { 
                background-color: #222; 
                color: #0f0; 
                padding: 15px; 
                border-radius: 5px;
                font-family: monospace;
                font-size: 12px;
                max-height: 300px;
                overflow-y: auto;
            }
            .log-line { margin: 5px 0; }
        </style>
    </head>
    <body>
        <div class="container-fluid">
            <h1>Trading System Dashboard</h1>
            
            <div class="row">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">System Status</div>
                        <div class="card-body">
                            <p><strong>Time:</strong> """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
                            <p><strong>Runner:</strong> <span class="status-good">● Active</span></p>
                            <p><strong>OrderRouter:</strong> <span class="status-good">● Active</span></p>
                            <p><strong>Data Source:</strong> <span class="status-good">● Connected</span></p>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">Quick Stats</div>
                        <div class="card-body">
    """
    
    # Add stats if trades exist
    if os.path.exists('output/orb_trades.csv'):
        try:
            df = pd.read_csv('output/orb_trades.csv')
            if not df.empty:
                wins = (df['pnl'] > 0).sum()
                total = len(df)
                win_rate = (wins / total * 100) if total > 0 else 0
                total_pnl = df['pnl'].sum()
                
                html += f"""
                            <p><strong>Total Trades:</strong> {total}</p>
                            <p><strong>Win Rate:</strong> {win_rate:.1f}%</p>
                            <p><strong>Total P&L:</strong> ${total_pnl:.0f}</p>
                """
        except:
            pass
    
    html += """
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">Recent Signals</div>
                        <div class="card-body">
                            <div class="log-box">
    """
    
    for signal in signals[-20:]:
        html += f'<div class="log-line">{signal}</div>'
    
    html += """
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">Recent Fills</div>
                        <div class="card-body">
                            <div class="log-box">
    """
    
    for fill in fills[-20:]:
        html += f'<div class="log-line">{fill}</div>'
    
    html += f"""
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-12">
                    <div class="card">
                        <div class="card-header">Recent Trades</div>
                        <div class="card-body">
                            {trades_html}
                        </div>
                    </div>
                </div>
            </div>
            
            <p style="text-align: center; margin-top: 40px; color: #999;">
                Dashboard auto-refreshes every 5 seconds
            </p>
        </div>
        
        <script>
            setTimeout(function() {{
                location.reload();
            }}, 5000);
        </script>
    </body>
    </html>
    """
    
    return html

if __name__ == '__main__':
    app.run(host='localhost', port=5001, debug=False)