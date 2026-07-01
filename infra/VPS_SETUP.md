# VPS Setup — Hosting NinjaTrader on a Windows VPS

NinjaTrader 8 only runs on Windows. If you're on Mac/Linux, you need a Windows VPS to host NT8.

**Recommended:** QuantVPS in Chicago (~$60/mo). Low latency to CME data feeds.

## Step 1: Rent VPS

1. Go to https://quantvps.com
2. Choose: **Windows Server 2019 or 2022, Chicago location**
3. Minimum specs:
   - CPU: 2 cores
   - RAM: 4 GB
   - Storage: 60 GB SSD
   - **High-speed connection (important for live trading)**

4. Pay, get credentials (IP, username, password)

## Step 2: Connect to VPS

**Windows laptop:** Remote Desktop (built-in)
1. Press Win+R, type `mstsc`
2. Enter VPS IP address
3. Login with credentials

**Mac:** Download Microsoft Remote Desktop from App Store
1. Launch, select "Add PC"
2. Enter VPS IP address
3. Login

**Linux:** Use Remmina or xfreerdp
```bash
xfreerdp /v:VPS_IP /u:USERNAME /p:PASSWORD
```

## Step 3: Configure Windows

Once logged into VPS:

**Disable updates:**
- Settings → Update & Security → Change active hours
- Active hours: 9:30 AM - 4:00 PM ET (never update during trading)

**Disable sleep:**
- Settings → System → Power & sleep
- Sleep: Never

**Disable screen lock (optional, for convenience):**
- Settings → Accounts → Sign-in options
- Require sign-in: Never

**Set timezone to Eastern (ET):**
- Date & time → Time zone: (UTC-05:00) Eastern Time

## Step 4: Install NT8 on VPS

1. Download NinjaTrader 8: https://ninjatrader.com/Download
2. Run installer on VPS
3. Sign up for NT8 account (if you don't have one)
4. Login with your credentials

## Step 5: Connect data feed on VPS

In NT8 on VPS:
1. Connections → Manage connections
2. Add Rithmic connection (or your preferred feed)
3. Enter login credentials
4. Test connection

## Step 6: Set up auto-restart

VPS can hiccup. Set up daily restart to keep it clean:

**Windows Task Scheduler:**
1. Press Win+R, type `taskschd.msc`
2. Create Basic Task → Name: "Restart NT8 Daily"
3. Trigger: Daily, 4:05 PM ET (after market close)
4. Action: Restart computer

This kills any zombie processes, keeps VPS fresh.

## Step 7: Pull your repo to VPS

Open PowerShell on VPS:
```powershell
cd C:\
git clone https://github.com/EthanGPT/algo-trading-system
cd algo-trading-system
```

Copy `.env` with your API keys.

## Step 8: Run live_runner on VPS (Python)

Install Python 3.9+ on VPS:
1. Download: https://www.python.org/downloads/
2. Run installer, check "Add Python to PATH"

Then:
```powershell
pip install -r requirements.txt
python bridge\live_runner.py
```

Keep this PowerShell window open (or use `nssm` to run as a service).

## Step 9: Verify bridge is wired

On VPS:
1. Open NT8
2. Create MES 09-26 chart
3. Add BarBridge indicator
4. Add OrderRouter strategy
5. Check: `data/live/MES_1m.csv` should be getting written every bar

On your laptop:
```bash
python bridge/live_runner.py
```

If it says "Polling data/live/MES_1m.csv", it's working. Signals will fire.

## Accessing VPS from your laptop

Your VPS runs live while you sleep. You can:

1. **Check logs remotely:**
   ```bash
   scp VPS_IP:C:/algo-trading-system/logs/runner.log .
   scp VPS_IP:C:/algo-trading-system/NT8-Logs/OrderRouter.log .
   ```

2. **Tail logs in real-time:**
   ```bash
   ssh USERNAME@VPS_IP "tail -f C:/algo-trading-system/logs/runner.log"
   ```

3. **RDP back into VPS** anytime to check NT8 status

## Cost breakdown

- QuantVPS: ~$60/mo
- Your laptop (local): $0 (you already have one)
- **Total: ~$60/mo after setup**

## Common issues

**"Can't connect to data feed on VPS"**
→ Check: 1) Internet speed on VPS (should be fast), 2) Firewall isn't blocking Rithmic, 3) Restart NT8

**"live_runner can't read CSV on VPS"**
→ Use full path: `C:/algo-trading-system/data/live/MES_1m.csv`

**"Remote connection drops"**
→ Normal. Reconnect. VPS keeps running in background.

**"High latency to data feed"**
→ QuantVPS in Chicago should be ~5-20ms to CME. If higher, restart connection.

## Pro tips

1. **Keep VPS log-in credential safe.** It's your trading system.
2. **Restart VPS weekly** (even if it seems fine). Keeps it healthy.
3. **Monitor VPS usage:** Task Manager → check CPU/RAM. If maxed out, your system will choke.
4. **Backup your code:** Push to GitHub regularly so you don't lose anything.