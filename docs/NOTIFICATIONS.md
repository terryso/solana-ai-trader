# Notification Setup Guide

This guide explains how to set up Telegram and Discord notifications for the Solana AI Trader.

**[简体中文](NOTIFICATIONS_CN.md) | English**

---

## Why Use Notifications?

Get instant alerts when:
- ✅ Trades are executed
- 📊 New trading signals are generated
- 💼 Portfolio updates
- 🚨 Errors occur
- 📈 Daily trading summaries

## Telegram Setup

### Step 1: Create a Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` command
3. Follow the prompts to name your bot (e.g., "My Trading Bot")
4. Copy the bot token (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Get Your Chat ID

1. Search for [@userinfobot](https://t.me/userinfobot) on Telegram
2. Send `/start` command
3. Copy your chat ID (looks like `123456789`)

### Step 3: Configure Environment Variables

Edit your `.env` file:

```bash
# Telegram Configuration
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

### Step 4: Test Connection

```bash
cd backend
python examples/notifications_example.py
```

You should receive a test message in Telegram!

## Discord Setup

### Step 1: Create Discord Webhook

1. Open your Discord server
2. Go to **Server Settings** → **Integrations**
3. Click **Webhooks** → **New Webhook**
4. Name it "Solana AI Trader"
5. Choose which channel to post to
6. Copy the webhook URL

### Step 2: Configure Environment Variables

Edit your `.env` file:

```bash
# Discord Configuration
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/123456789/ABCdefGHIjklMNOpqrsTUVwxyz
```

### Step 3: Test Connection

```bash
cd backend
python examples/notifications_example.py
```

You should receive a test message in Discord!

## Notification Types

### Trade Notifications
Sent whenever a trade is executed:
```
🟢 Trade ✅

Type: BUY
Token: SOL
Amount: 10.500000
Price: $145.50
Value: $1,527.75
Status: EXECUTED

Tx: `abc123...xyz789`
```

### Signal Notifications
Sent when LLM generates a new trading signal:
```
🟢 New Trading Signal

Action: BUY
Token: BONK
Strength: strong
Confidence: 85%
Risk: medium

Analysis: RSI indicates oversold conditions...
```

### Portfolio Updates
```
💼 Portfolio Update

Total Value: $5,432.10
Unrealized PnL: 📈 +$234.50 (+4.51%)
Open Positions: 3
```

### Daily Summaries
```
📊 Daily Trading Summary

Total Trades: 15
Total Bought: $3,200.00
Total Sold: $3,434.50
Net PnL: 📈 +$234.50
```

## Advanced Configuration

### Silent Notifications

To send notifications without sound:

```python
await telegram.send_message(
    text='Silent update',
    disable_notification=True
)
```

### Custom Messages

```python
from src.services.notifications import get_telegram_notifier

telegram = get_telegram_notifier()
await telegram.send_message(
    text='<b>Custom message</b> with <i>formatting</i>',
    parse_mode='HTML'
)
```

### Discord Embeds

```python
from src.services.notifications import get_discord_notifier

discord = get_discord_notifier()
await discord.send_message(
    embeds=[{
        'title': 'Custom Embed',
        'description': 'With custom fields',
        'color': 0x00ff00,
        'fields': [
            {'name': 'Field 1', 'value': 'Value 1'},
            {'name': 'Field 2', 'value': 'Value 2'}
        ]
    }]
)
```

## Best Practices

1. **Use both Telegram and Discord** for redundancy
2. **Test notifications** before deploying to production
3. **Keep chat IDs secure** - never commit to git
4. **Use dedicated channels** for trading alerts
5. **Set up notification filtering** in Discord if needed

## Troubleshooting

### Telegram: "Bad Token" Error
- Verify bot token is correct
- Check bot wasn't deleted by BotFather
- Ensure token has no extra spaces

### Telegram: "Chat Not Found"
- Verify chat ID is correct
- Start a conversation with your bot first (send /start)
- Check bot has permission to message you

### Discord: Webhook Not Working
- Verify webhook URL is complete
- Check webhook wasn't deleted
- Ensure bot has permission to post in channel

### No Notifications Received
- Check `.env` file is loaded correctly
- Verify API keys are set
- Check logs for errors: `tail -f logs/trading.log`

## Security Tips

1. **Never share** your bot tokens or webhook URLs
2. **Use environment variables** - never hardcode
3. **Rotate tokens** periodically if needed
4. **Limit bot permissions** in Telegram
5. **Use dedicated webhooks** for each environment

## Example Integration

The notification system is automatically integrated into:

- **Trading Manager**: Sends notifications on trade execution
- **Signal Service**: Sends notifications on new signals
- **Error Handlers**: Sends alerts on critical errors

No additional code needed - just configure your credentials!
