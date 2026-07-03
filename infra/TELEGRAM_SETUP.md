# Telegram Setup — Alerts on Your Phone

Optional. Telegram notifies you when trades execute, errors occur, or drawdown approaches limits. No screens needed.

## Step 1: Create a Telegram Bot

1. Open Telegram (app or telegram.org)
2. Search for **BotFather** (official Telegram bot manager)
3. Start chat, type `/start`
4. Type `/newbot`
5. BotFather asks for a name: e.g., "MyTradingBot"
6. BotFather asks for username: e.g., "my_trading_bot_xyz" (must be unique)
7. BotFather gives you a **token** (long string). Copy it.
8. Paste into `.env`: `TELEGRAM_BOT_TOKEN=<your_token>`

## Step 2: Get Your Chat ID

1. Search for **userinfobot** in Telegram
2. Start chat, type `/start`
3. It shows your **User ID** (a number)
4. Paste into `.env`: `TELEGRAM_CHAT_ID=<your_user_id>`

## Step 3: Start the Bot

1. Go back to your bot's chat
2. Type something (anything) to start the conversation
3. Now the bot can send you messages

## Step 4: Wire Into live_runner

In `bridge/live_runner.py`, add at the top:

```python
import requests

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def send_telegram(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message
    }
    
    try:
        requests.post(url, data=data, timeout=5)
    except:
        pass  # Telegram is optional, don't crash if it fails
```

Then when a signal fires:

```python
if signal['action'] != 'FLAT':
    send_telegram(f"Signal: {signal['action']} {instrument} @ {current_bar['close']}")
```

And when a fill comes back:

```python
send_telegram(f"Fill: {side} {quantity} @ {fill_price}")
```

## Step 5: Optional — Alerts for Errors & Drawdown

Add these anywhere live_runner detects a problem:

```python
# Connection lost
send_telegram("⚠️ Data feed disconnected")

# Drawdown approaching limit
if current_drawdown > max_drawdown * 0.9:
    send_telegram(f"⚠️ Drawdown at 90%: ${current_drawdown}")

# Max daily loss hit
if daily_loss <= -max_daily_loss:
    send_telegram(f"🛑 Max daily loss hit: ${daily_loss}")
```

## Testing

Send a test message:

```python
send_telegram("Test: System is live")
```

Check your Telegram — you should see it instantly.

## That's it

You're now getting trade alerts on your phone. No monitoring needed.