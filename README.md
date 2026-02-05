# Solana AI Trader

Automated Solana trading system powered by LLM analysis.

## Features

- Real-time Solana blockchain monitoring
- LLM-powered trading signal generation
- Automated trade execution via Jupiter
- Comprehensive risk management
- Paper trading mode for testing

## Project Structure

```
solana-ai-trader/
├── backend/
│   ├── src/
│   │   ├── config/         # Configuration management
│   │   ├── database/       # Database models and connection
│   │   ├── services/       # Core services (Solana, Jupiter, LLM)
│   │   ├── models/         # Pydantic models
│   │   └── utils/          # Utilities and logging
│   ├── logs/               # Application logs
│   ├── data/               # Database files
│   ├── requirements.txt
│   ├── .env.example
│   └── main.py
└── README.md
```

## Installation

1. Clone the repository:
```bash
cd ~/solana-ai-trader
```

2. Create virtual environment:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

## Configuration

Edit `.env` file with your settings:

### Required for Development
- No API keys needed for basic testing

### Required for Trading
- `SOLANA_WALLET_PRIVATE_KEY`: Your wallet private key
- `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`: LLM provider key

### Optional but Recommended
- `HELIUS_RPC_URL`: Better Solana RPC performance
- `TELEGRAM_BOT_TOKEN`: For trade notifications

## Usage

### Web Dashboard (Recommended)

Start the web interface:
```bash
cd backend
python run_server.py
```

Then open: http://localhost:8000

The web dashboard includes:
- Real-time portfolio monitoring
- Trade history
- Trading signals
- Auto-refresh functionality
- Responsive design

### CLI Mode

#### Development Mode (Testing)
```bash
cd backend
python main.py
```

#### Paper Trading Mode
```bash
# Set ENVIRONMENT=paper_trading in .env
python main.py
```

#### Production Mode
```bash
# Set ENVIRONMENT=production in .env
python main.py
```

## Risk Management

Default risk limits:
- Maximum position: 5% of portfolio
- Daily loss limit: 2%
- Stop loss: 10%
- Maximum open positions: 3

**WARNING:** Start with paper trading mode and small amounts!

## API Examples

### Price Query
```python
from src.services import get_market_data_client

client = get_market_data_client()
sol_price = await client.get_sol_price()
print(f'SOL Price: ${sol_price}')
```

### Execute Trade
```python
from src.services import get_trading_manager

manager = get_trading_manager()
trade = await manager.execute_trade_with_validation(
    token_mint='EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
    token_symbol='USDC',
    amount_sol=1.0,
    trade_type=TradeType.BUY
)
```

### Get Portfolio
```python
portfolio = await manager.get_portfolio_value()
print(f'Total Value: ${portfolio.total_value_usd}')
print(f'PnL: {portfolio.unrealized_pnl_percentage:.2f}%')
```

Run examples:
```bash
python examples/trading_example.py
python examples/llm_analysis_example.py
python examples/notifications_example.py
```

## Deployment

### Docker (Recommended)

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Manual Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions including:
- Automated installation script
- Systemd service setup
- Nginx reverse proxy
- SSL/TLS configuration
- Production best practices

Quick start:
```bash
# Run installation script
sudo bash deploy/install.sh

# Start service
sudo systemctl start solana-ai-trader

# Check status
sudo systemctl status solana-ai-trader
```

## Documentation

- [USER_MANUAL.md](USER_MANUAL.md) - Complete user guide
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide
- [NOTIFICATIONS.md](NOTIFICATIONS.md) - Notification setup

## Roadmap

- [x] Project structure
- [x] Database models
- [x] Solana RPC client
- [x] Jupiter integration
- [x] LLM analysis engine
- [x] Technical indicators (15+ indicators)
- [x] Trading signal generation
- [x] Web monitoring dashboard
- [x] Telegram/Discord notifications
- [x] Docker deployment
- [x] Production deployment scripts
- [ ] Backtesting system
- [ ] Advanced strategies

## License

MIT

## Disclaimer

This software is for educational purposes only. Cryptocurrency trading involves substantial risk of loss. Use at your own risk.
