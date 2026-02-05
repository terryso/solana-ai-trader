# Solana AI Trader - User Manual

Complete guide to using the Solana AI Trader system.

---

## Table of Contents

1. [Introduction](#introduction)
2. [Quick Start Guide](#quick-start-guide)
3. [Configuration](#configuration)
4. [Using the Web Dashboard](#using-the-web-dashboard)
5. [Trading Strategies](#trading-strategies)
6. [Risk Management](#risk-management)
7. [Notifications](#notifications)
8. [API Reference](#api-reference)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

---

## Introduction

### What is Solana AI Trader?

Solana AI Trader is an automated trading system that:
- Uses Large Language Models (LLM) to analyze market conditions
- Executes trades on the Solana blockchain via Jupiter
- Provides real-time monitoring through a web dashboard
- Sends notifications to Telegram/Discord
- Implements comprehensive risk management

### Key Features

- **AI-Powered Analysis**: Leverages Claude/OpenAI for intelligent trading decisions
- **15+ Technical Indicators**: RSI, MACD, Bollinger Bands, and more
- **Automated Trading**: Execute trades 24/7 based on AI signals
- **Risk Management**: Configurable limits to protect your capital
- **Real-Time Monitoring**: Web dashboard with live updates
- **Notifications**: Instant alerts for trades and signals
- **Paper Trading**: Test strategies without risking real money

### System Architecture

```
┌─────────────────┐
│   Web Dashboard │
└────────┬────────┘
         │
┌────────▼────────┐
│  FastAPI Server │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐  ┌─▼──────────┐
│  LLM  │  │  Jupiter   │
│Engine │  │   Trading  │
└───┬───┘  └─┬──────────┘
    │        │
┌───▼────────▼───┐
│ Solana RPC     │
└────────────────┘
```

---

## Quick Start Guide

### Installation (5 minutes)

1. **Install dependencies:**
```bash
# Install Python 3.11
sudo apt-get install python3.11 python3.11-venv git
```

2. **Clone and setup:**
```bash
cd ~
git clone <repository_url> solana-ai-trader
cd solana-ai-trader/backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Configure:**
```bash
cp .env.example .env
nano .env
```

Minimum configuration:
```bash
ENVIRONMENT=paper_trading  # Start with paper trading
ANTHROPIC_API_KEY=your_key_here  # For LLM analysis
```

4. **Start:**
```bash
python run_server.py
```

5. **Access dashboard:**
```
http://localhost:8000
```

### First Trade

1. **Generate a signal:**
```python
from src.services import get_signal_service
import asyncio

async def get_signal():
    service = get_signal_service()
    signal = await service.generate_signal(
        token_address='So11111111111111111111111111111111111111112',
        token_symbol='SOL',
        price_history=[]  # Optional
    )
    print(f"Action: {signal.action}")
    print(f"Confidence: {signal.confidence}")
    print(f"Reasoning: {signal.reasoning}")

asyncio.run(get_signal())
```

2. **Execute trade** (if signal is good):
```python
from src.services import get_trading_manager
from src.models import TradeType

async def execute_trade():
    manager = get_trading_manager()
    trade = await manager.execute_trade_with_validation(
        token_mint='EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
        token_symbol='USDC',
        amount_sol=1.0,
        trade_type=TradeType.BUY
    )
    print(f"Trade executed: {trade}")

asyncio.run(execute_trade())
```

---

## Configuration

### Environment Variables

Create a `.env` file in the `backend` directory:

#### Essential Settings

```bash
# Environment
ENVIRONMENT=development  # development | paper_trading | production

# Solana Configuration
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
HELIUS_RPC_URL=  # Optional but recommended

# Wallet (Production only)
SOLANA_WALLET_PRIVATE_KEY=  # Your wallet private key

# LLM Configuration
ANTHROPIC_API_KEY=  # For Claude
OPENAI_API_KEY=  # For GPT (alternative)
LLM_PROVIDER=anthropic  # anthropic | openai
LLM_MODEL=claude-3-5-sonnet-20241022
```

#### Risk Management

```bash
# Position Sizing
MAX_POSITION_SIZE=0.05  # Max 5% of portfolio per trade
MAX_OPEN_POSITIONS=3    # Maximum concurrent positions
MIN_TRADE_AMOUNT_SOL=0.01  # Minimum trade size

# Stop Loss & Limits
STOP_LOSS_PERCENTAGE=0.10  # 10% stop loss
MAX_DAILY_LOSS=0.02  # Stop trading after 2% daily loss

# Trading Parameters
TRADE_SLIPPAGE=0.01  # 1% slippage tolerance
RESERVE_BALANCE_SOL=0.01  # Keep 0.01 SOL for fees
```

#### Notifications

```bash
# Telegram
TELEGRAM_BOT_TOKEN=  # From @BotFather
TELEGRAM_CHAT_ID=  # From @userinfobot

# Discord
DISCORD_WEBHOOK_URL=  # From server settings
```

### Recommended Configurations

#### For Testing/Development
```bash
ENVIRONMENT=development
LLM_PROVIDER=anthropic
# No wallet needed
```

#### For Paper Trading
```bash
ENVIRONMENT=paper_trading
LLM_PROVIDER=anthropic
# Simulates trades without real money
```

#### For Production (Small Account)
```bash
ENVIRONMENT=production
MAX_POSITION_SIZE=0.02  # 2% per trade
MAX_DAILY_LOSS=0.01  # 1% daily limit
MAX_OPEN_POSITIONS=2
MIN_TRADE_AMOUNT_SOL=0.05
STOP_LOSS_PERCENTAGE=0.08
```

#### For Production (Large Account)
```bash
ENVIRONMENT=production
MAX_POSITION_SIZE=0.05  # 5% per trade
MAX_DAILY_LOSS=0.03  # 3% daily limit
MAX_OPEN_POSITIONS=5
MIN_TRADE_AMOUNT_SOL=0.1
STOP_LOSS_PERCENTAGE=0.12
```

---

## Using the Web Dashboard

### Overview

The web dashboard provides real-time monitoring and control of your trading bot.

### Accessing the Dashboard

1. **Start the server:**
```bash
cd backend
python run_server.py
```

2. **Open browser:**
```
http://localhost:8000
```

### Dashboard Sections

#### 1. Statistics Cards

Top section displays 4 key metrics:
- **Portfolio Value**: Total value in USD
- **Available Balance**: SOL available for trading
- **Daily PnL**: Today's profit/loss
- **Signals Today**: Number of signals generated

Color coding:
- 🟢 Green: Profit
- 🔴 Red: Loss
- ⚪ Gray: Neutral

#### 2. Portfolio Tab

Shows current open positions:
- Token symbol and amount
- Entry price vs current price
- Unrealized PnL (amount and percentage)
- Position age

Example:
```
SOL   10.5 @ $145.50
Current: $152.30
PnL: +$71.40 (+4.67%)
```

#### 3. Trade History Tab

Lists all executed trades:
- Timestamp
- Type (BUY/SELL)
- Token
- Amount
- Price
- Value (USD)
- Status (pending/executed/failed)

#### 4. Signals Tab

Shows AI-generated trading signals:
- Timestamp
- Action (buy/sell/hold)
- Signal strength
- Confidence level
- Risk assessment
- LLM reasoning

### Auto-Refresh

Configure automatic data refresh:
- Off: Manual refresh only
- 5 seconds: Real-time monitoring
- 15 seconds: Balanced (default)
- 30 seconds: Reduced API calls
- 1 minute: Minimal updates

### Interpreting Signals

**Signal Strength:**
- `very_strong`: High conviction, consider trading
- `strong`: Good opportunity
- `moderate`: Some potential
- `weak`: Low conviction
- `very_weak`: Ignore

**Confidence Level:**
- `> 80%`: High confidence
- `60-80%`: Moderate confidence
- `< 60%`: Low confidence, skip trade

**Risk Level:**
- `low`: Safer trades
- `medium`: Standard risk
- `high`: Risky, skip in production

---

## Trading Strategies

### Built-in Strategy: AI Signal Following

The system uses LLM analysis to generate signals based on:
- Technical indicators (RSI, MACD, etc.)
- Price action patterns
- Volume analysis
- Market conditions

### Strategy Workflow

1. **Data Collection**
   - Fetch current price
   - Get 24h volume and change
   - Calculate technical indicators

2. **LLM Analysis**
   - Send data to Claude/GPT
   - Get trading recommendation
   - Receive reasoning and confidence

3. **Signal Evaluation**
   - Check confidence threshold (>60%)
   - Verify risk level (not "high" in production)
   - Validate signal strength (not "weak")

4. **Trade Execution**
   - Calculate position size
   - Validate against risk limits
   - Execute via Jupiter
   - Send notification

### Custom Strategy Example

```python
from src.services import get_signal_service, get_trading_manager
from src.models import TradeType
import asyncio

async def custom_strategy():
    """Custom strategy: Trade only on strong signals."""

    signal_service = get_signal_service()
    trading_manager = get_trading_manager()

    # Generate signal
    signal = await signal_service.generate_signal(
        token_address='So11111111111111111111111111111111111111112',
        token_symbol='SOL'
    )

    # Custom criteria
    if (signal.action == 'buy' and
        signal.confidence > 0.75 and
        signal.strength in ['strong', 'very_strong'] and
        signal.risk_level != 'high'):

        # Calculate position (more aggressive on high confidence)
        base_amount = 1.0  # SOL
        multiplier = 1 + (signal.confidence - 0.75)  # Up to 1.25x
        amount = base_amount * multiplier

        # Execute
        trade = await trading_manager.execute_trade_with_validation(
            token_mint=signal.token_address,
            token_symbol=signal.token_symbol,
            amount_sol=amount,
            trade_type=TradeType.BUY
        )

        print(f"Trade executed: {trade}")
    else:
        print("Signal does not meet criteria")

asyncio.run(custom_strategy())
```

### Multi-Token Strategy

```python
async def monitor_multiple_tokens():
    """Monitor and trade multiple tokens."""

    tokens = [
        ('So11111111111111111111111111111111111111112', 'SOL'),
        ('EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'USDC'),
        ('Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB', 'USDT'),
    ]

    signal_service = get_signal_service()
    trading_manager = get_trading_manager()

    for address, symbol in tokens:
        signal = await signal_service.generate_signal(
            token_address=address,
            token_symbol=symbol
        )

        if signal.action == 'buy' and signal.confidence > 0.7:
            await trading_manager.execute_trade_with_validation(
                token_mint=address,
                token_symbol=symbol,
                amount_sol=0.5,
                trade_type=TradeType.BUY
            )
```

---

## Risk Management

### Built-in Risk Controls

#### 1. Position Sizing

Limits how much you invest in a single trade:
```bash
MAX_POSITION_SIZE=0.05  # 5% of portfolio
```

Example:
- Portfolio: $1000
- Max per trade: $50

#### 2. Daily Loss Limit

Stops trading if daily loss exceeds threshold:
```bash
MAX_DAILY_LOSS=0.02  # 2% daily
```

Example:
- Portfolio: $1000
- Trading stops after: $20 loss

#### 3. Stop Loss

Automatically sells if price drops:
```bash
STOP_LOSS_PERCENTAGE=0.10  # 10% stop loss
```

Example:
- Buy at: $100
- Stop loss triggers at: $90

#### 4. Position Limits

Maximum number of concurrent positions:
```bash
MAX_OPEN_POSITIONS=3
```

#### 5. Minimum Trade Size

Prevents very small trades:
```bash
MIN_TRADE_AMOUNT_SOL=0.01  # 0.01 SOL minimum
```

### Custom Risk Management

```python
async def safe_trade():
    """Trade with additional safety checks."""

    trading_manager = get_trading_manager()

    # Check daily loss
    if trading_manager.should_stop_trading():
        print("Daily loss limit reached, not trading")
        return

    # Get portfolio
    portfolio = await trading_manager.get_portfolio_value()

    # Check available balance
    if portfolio.available_balance_sol < 0.1:
        print("Insufficient balance")
        return

    # Check position count
    if len(portfolio.positions) >= 3:
        print("Too many open positions")
        return

    # Execute trade
    trade = await trading_manager.execute_trade_with_validation(
        token_mint='EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
        token_symbol='USDC',
        amount_sol=1.0,
        trade_type=TradeType.BUY
    )
```

### Risk Levels Explained

**Low Risk:**
- Stable tokens (SOL, USDC)
- High liquidity
- Lower returns expected

**Medium Risk:**
- Established tokens
- Good liquidity
- Moderate risk/reward

**High Risk:**
- New/meme tokens
- Low liquidity
- High volatility
- Skip in production mode

---

## Notifications

### Setting Up Telegram

1. **Create Bot:**
   - Open Telegram
   - Search for @BotFather
   - Send `/newbot`
   - Follow instructions
   - Copy bot token

2. **Get Chat ID:**
   - Search for @userinfobot
   - Send `/start`
   - Copy your chat ID

3. **Configure:**
```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHI
TELEGRAM_CHAT_ID=123456789
```

4. **Test:**
```python
from src.services.notifications import get_telegram_notifier
import asyncio

async def test():
    notifier = get_telegram_notifier()
    await notifier.test_connection()

asyncio.run(test())
```

### Setting Up Discord

1. **Create Webhook:**
   - Server Settings → Integrations
   - Webhooks → New Webhook
   - Copy webhook URL

2. **Configure:**
```bash
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

3. **Test:**
```python
from src.services.notifications import get_discord_notifier
import asyncio

async def test():
    notifier = get_discord_notifier()
    await notifier.test_connection()

asyncio.run(test())
```

### Notification Types

**Trade Notifications:**
- Sent when trade executes
- Includes all details
- Transaction signature link

**Signal Notifications:**
- Sent when AI generates signal
- Includes full analysis
- Confidence and risk level

**Error Alerts:**
- Critical errors only
- Context and details
- Immediate attention required

**Daily Summary:**
- End of day recap
- Total trades
- Net PnL
- Best/worst trades

---

## API Reference

### Trading Manager

#### Get Portfolio
```python
from src.services import get_trading_manager

manager = get_trading_manager()
portfolio = await manager.get_portfolio_value()
```

#### Execute Trade
```python
from src.models import TradeType

trade = await manager.execute_trade_with_validation(
    token_mint='EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
    token_symbol='USDC',
    amount_sol=1.0,
    trade_type=TradeType.BUY
)
```

#### Get Trade History
```python
trades = manager.get_trade_history(limit=50)
```

#### Get Daily PnL
```python
pnl = manager.get_daily_pnl()
print(f"Daily PnL: ${pnl['pnl_usd']}")
```

### Signal Service

#### Generate Signal
```python
from src.services import get_signal_service

service = get_signal_service()
signal = await service.generate_signal(
    token_address='So11111111111111111111111111111111111111112',
    token_symbol='SOL'
)
```

#### Get Signal History
```python
signals = service.get_recent_signals(limit=50)
```

### Market Data

#### Get Token Price
```python
from src.services import get_market_data_client

client = get_market_data_client()
price = await client.get_token_price('token_address')
```

#### Get SOL Price
```python
sol_price = await client.get_sol_price()
```

### REST API Endpoints

#### Get Portfolio
```
GET /api/portfolio
```

#### Get Trades
```
GET /api/trades?limit=100&token_address=...
```

#### Get Signals
```
GET /api/signals?limit=50&token_address=...
```

#### Get Statistics
```
GET /api/stats
```

#### Health Check
```
GET /api/health
```

---

## Troubleshooting

### Common Issues

#### 1. Service Won't Start

**Problem:** Service fails to start

**Solutions:**
```bash
# Check logs
sudo journalctl -u solana-ai-trader -n 50

# Check port availability
sudo netstat -tlnp | grep 8000

# Verify Python version
python --version  # Should be 3.11+

# Check dependencies
source venv/bin/activate
pip list
```

#### 2. "Module Not Found" Error

**Problem:** Import errors

**Solution:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

#### 3. Database Locked

**Problem:** SQLite database locked

**Solution:**
```bash
# Stop service
sudo systemctl stop solana-ai-trader

# Check for locks
lsof backend/data/*.db

# Remove locks if needed
rm backend/data/*.db-journal

# Restart
sudo systemctl start solana-ai-trader
```

#### 4. API Rate Limits

**Problem:** Too many RPC requests

**Solutions:**
```bash
# Use Helius RPC (higher limits)
HELIUS_RPC_URL=https://your-helius-url

# Reduce API call frequency
# Adjust polling intervals
```

#### 5. LLM API Errors

**Problem:** Claude/OpenAI API failures

**Solutions:**
```bash
# Verify API key
echo $ANTHROPIC_API_KEY

# Check quota
# Visit provider dashboard

# Switch providers
LLM_PROVIDER=openai  # or anthropic
```

#### 6. Trade Execution Failed

**Problem:** Trades not executing

**Checks:**
```python
# 1. Check environment
ENVIRONMENT=development  # Trades won't execute in dev mode

# 2. Check wallet balance
from src.services import get_trading_executor
executor = get_trading_executor()
balance = await executor.get_wallet_balance()
print(f"Balance: {balance} SOL")

# 3. Check validation
is_valid, error = await executor.validate_trade(
    amount=1.0,
    token_mint='...'
)
print(f"Valid: {is_valid}, Error: {error}")
```

### Getting Help

1. **Check Logs:**
```bash
# Application logs
tail -f logs/trading.log

# Service logs
sudo journalctl -u solana-ai-trader -f
```

2. **Test Configuration:**
```bash
cd backend
source venv/bin/activate
python -c "from src.config import settings; print(settings)"
```

3. **Run Diagnostics:**
```bash
python examples/trading_example.py
python examples/llm_analysis_example.py
```

---

## Best Practices

### 1. Start Small

**Always begin with paper trading:**
```bash
ENVIRONMENT=paper_trading
```

**Use small amounts in production:**
- Start with 0.1 SOL per trade
- Gradually increase as you gain confidence
- Never risk more than you can afford to lose

### 2. Monitor Regularly

**Check dashboard daily:**
- Review executed trades
- Verify signal quality
- Monitor PnL

**Set up notifications:**
- Get instant alerts on trades
- Receive error notifications
- Daily summary emails

### 3. Risk Management

**Conservative settings:**
```bash
MAX_POSITION_SIZE=0.02  # 2% per trade
MAX_DAILY_LOSS=0.01  # 1% daily limit
STOP_LOSS_PERCENTAGE=0.08  # 8% stop loss
```

**Diversify:**
- Trade multiple tokens
- Don't put all funds in one position
- Keep some SOL reserved for fees

### 4. Signal Quality

**Filter signals:**
```python
# Only trade high confidence signals
if signal.confidence > 0.75:
    execute_trade()
```

**Review LLM reasoning:**
- Understand why signal was generated
- Learn from good/bad calls
- Adjust strategy accordingly

### 5. Maintenance

**Regular updates:**
```bash
# Update code
git pull
pip install -r requirements.txt --upgrade

# Restart service
sudo systemctl restart solana-ai-trader
```

**Backups:**
```bash
# Backup database and config
tar -czf backup-$(date +%Y%m%d).tar.gz \
    backend/data/ \
    backend/.env
```

**Database cleanup:**
```bash
# Keep last 1000 trades
sqlite3 backend/data/trading.db \
    "DELETE FROM trades WHERE id NOT IN (
        SELECT id FROM trades ORDER BY timestamp DESC LIMIT 1000
    );"
```

### 6. Security

**Protect credentials:**
```bash
# Never commit .env to git
echo ".env" >> .gitignore

# Use restrictive permissions
chmod 600 .env
```

**Use dedicated wallet:**
- Create separate wallet for trading
- Only deposit funds you're willing to trade
- Enable additional security if available

### 7. Performance

**Optimize API calls:**
```bash
# Use Helius RPC
HELIUS_RPC_URL=https://...

# Adjust refresh intervals
# Don't poll too frequently
```

**Monitor resources:**
```bash
# Check CPU/memory
htop

# Check disk space
df -h
```

### 8. Testing

**Test everything:**
```bash
# 1. Test signals
python examples/llm_analysis_example.py

# 2. Test notifications
python examples/notifications_example.py

# 3. Test trading
python examples/trading_example.py

# 4. Test web interface
python run_server.py
# Then open http://localhost:8000
```

---

## Advanced Usage

### Custom Signal Filtering

```python
async def custom_signal_filter():
    service = get_signal_service()

    signal = await service.generate_signal(...)

    # Custom filters
    filters = [
        signal.confidence > 0.7,
        signal.risk_level != 'high',
        signal.strength in ['strong', 'very_strong'],
        # Add your criteria
    ]

    if all(filters):
        return True
    return False
```

### Scheduled Trading

```python
import asyncio
from datetime import datetime

async def scheduled_trading():
    """Run trading analysis every hour."""

    while True:
        # Generate and evaluate signals
        signal = await service.generate_signal(...)

        if meets_criteria(signal):
            await execute_trade(signal)

        # Wait 1 hour
        await asyncio.sleep(3600)
```

### Batch Processing

```python
async def analyze_multiple_tokens():
    """Analyze multiple tokens in parallel."""

    tokens = [...]  # Your token list

    tasks = [
        service.generate_signal(addr, sym)
        for addr, sym in tokens
    ]

    signals = await asyncio.gather(*tasks)

    # Process signals
    for signal in signals:
        if signal.confidence > 0.8:
            print(f"High confidence signal: {signal.token_symbol}")
```

---

## Support

### Documentation

- [README.md](README.md) - Project overview
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide
- [NOTIFICATIONS.md](NOTIFICATIONS.md) - Notification setup

### Examples

- `examples/trading_example.py` - Trading examples
- `examples/llm_analysis_example.py` - LLM analysis
- `examples/notifications_example.py` - Notification tests

### Getting Help

1. Check this manual first
2. Review logs for errors
3. Test with examples
4. Check documentation

### Disclaimer

This software is for educational purposes only. Cryptocurrency trading involves substantial risk of loss.

**Important:**
- Always start with paper trading
- Never invest more than you can afford to lose
- Understand the risks before using real money
- Past performance does not guarantee future results

**You are solely responsible for your trading decisions and outcomes.**

---

## Version History

- **v0.1.0** - Initial release
  - Core trading functionality
  - LLM analysis engine
  - Web dashboard
  - Notifications
  - Risk management

---

**Last Updated:** 2025-02-05

**For the latest updates and documentation, visit the GitHub repository.**
