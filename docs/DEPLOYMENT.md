# Deployment Guide

This guide covers deploying Solana AI Trader to production.

**[简体中文](DEPLOYMENT_CN.md) | English**

---

## Table of Contents

1. [Quick Start (Docker)](#quick-start-docker)
2. [Manual Deployment](#manual-deployment)
3. [Production Configuration](#production-configuration)
4. [SSL/TLS Setup](#ssltls-setup)
5. [Monitoring and Maintenance](#monitoring-and-maintenance)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start (Docker)

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+

### Steps

1. **Clone repository:**
```bash
git clone <repository_url>
cd solana-ai-trader
```

2. **Configure environment:**
```bash
cp backend/.env.example backend/.env
nano backend/.env  # Edit with your configuration
```

3. **Start with Docker Compose:**
```bash
docker-compose up -d
```

4. **Check logs:**
```bash
docker-compose logs -f solana-ai-trader
```

5. **Access dashboard:**
```
http://localhost:8000
```

### With Nginx Reverse Proxy

```bash
docker-compose --profile with-nginx up -d
```

Access via: `http://localhost`

---

## Manual Deployment

### System Requirements

- **OS:** Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- **Python:** 3.11+
- **RAM:** 2GB minimum, 4GB recommended
- **Storage:** 20GB minimum
- **Network:** Stable internet connection

### Automated Installation

1. **Run installation script:**
```bash
sudo bash deploy/install.sh
```

2. **Edit configuration:**
```bash
sudo nano /home/trader/solana-ai-trader/backend/.env
```

3. **Start service:**
```bash
sudo systemctl start solana-ai-trader
```

### Manual Installation

1. **Install system dependencies:**

Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3-pip git nginx
```

CentOS/RHEL:
```bash
sudo yum install -y python311 python311-pip git nginx
```

2. **Create user:**
```bash
sudo useradd -m -s /bin/bash trader
```

3. **Setup application:**
```bash
# Create directory
sudo mkdir -p /home/trader/solana-ai-trader
sudo chown trader:trader /home/trader/solana-ai-trader

# Clone repository (or copy files)
cd /home/trader
git clone <repository_url> solana-ai-trader
# OR
# sudo cp -r /path/to/solana-ai-trader /home/trader/

# Setup virtual environment
cd solana-ai-trader/backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
cp .env.example .env
nano .env
```

5. **Setup systemd service:**
```bash
sudo cp deploy/solana-ai-trader.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable solana-ai-trader
```

6. **Start service:**
```bash
sudo systemctl start solana-ai-trader
```

---

## Production Configuration

### Environment Variables

Edit `.env` file with production settings:

```bash
# Environment
ENVIRONMENT=production

# Solana RPC
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
HELIUS_RPC_URL=https://your-helius-rpc-url  # Recommended

# Wallet (NEVER commit to git)
SOLANA_WALLET_PRIVATE_KEY=your_private_key

# LLM API
ANTHROPIC_API_KEY=your_anthropic_key
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-sonnet-20241022

# Notifications
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Risk Management
MAX_POSITION_SIZE=0.05  # 5% per trade
MAX_DAILY_LOSS=0.02     # 2% daily loss limit
STOP_LOSS_PERCENTAGE=0.10
MAX_OPEN_POSITIONS=3
```

### Security Best Practices

1. **File Permissions:**
```bash
sudo chmod 600 /home/trader/solana-ai-trader/backend/.env
sudo chown trader:trader /home/trader/solana-ai-trader/backend/.env
```

2. **Firewall Configuration:**
```bash
# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow SSH
sudo ufw allow 22/tcp

# Enable firewall
sudo ufw enable
```

3. **Use Helius RPC:**
- Higher rate limits
- Better reliability
- Lower latency

---

## SSL/TLS Setup

### Using Let's Encrypt (Certbot)

1. **Install Certbot:**
```bash
sudo apt-get install certbot python3-certbot-nginx
```

2. **Obtain certificate:**
```bash
sudo certbot --nginx -d your-domain.com
```

3. **Auto-renewal:**
```bash
sudo certbot renew --dry-run
```

### Manual SSL Setup

1. **Generate SSL certificate:**
```bash
sudo mkdir -p /etc/nginx/ssl
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/key.pem \
  -out /etc/nginx/ssl/cert.pem
```

2. **Update nginx.conf:**
Uncomment HTTPS section and update paths.

3. **Restart nginx:**
```bash
sudo systemctl restart nginx
```

---

## Monitoring and Maintenance

### Check Service Status

```bash
sudo systemctl status solana-ai-trader
```

### View Logs

**Live logs:**
```bash
sudo journalctl -u solana-ai-trader -f
```

**Application logs:**
```bash
tail -f /home/trader/solana-ai-trader/logs/output.log
tail -f /home/trader/solana-ai-trader/logs/error.log
```

**Docker logs:**
```bash
docker-compose logs -f
```

### Restart Service

```bash
sudo systemctl restart solana-ai-trader
```

### Update Application

**Using update script:**
```bash
sudo bash deploy/update.sh
```

**Manual update:**
```bash
sudo systemctl stop solana-ai-trader
cd /home/trader/solana-ai-trader
git pull
cd backend
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl start solana-ai-trader
```

### Backup

**Backup database and configuration:**
```bash
tar -czf backup-$(date +%Y%m%d).tar.gz \
  /home/trader/solana-ai-trader/backend/data \
  /home/trader/solana-ai-trader/backend/.env
```

**Restore:**
```bash
tar -xzf backup-YYYYMMDD.tar.gz -C /
```

---

## Troubleshooting

### Service won't start

1. **Check logs:**
```bash
sudo journalctl -u solana-ai-trader -n 50
```

2. **Verify configuration:**
```bash
cd /home/trader/solana-ai-trader/backend
source venv/bin/activate
python -c "from src.config import settings; print(settings)"
```

3. **Check port availability:**
```bash
sudo netstat -tlnp | grep 8000
```

### Database errors

1. **Check database file:**
```bash
ls -la /home/trader/solana-ai-trader/backend/data/
```

2. **Recreate database:**
```bash
rm /home/trader/solana-ai-trader/backend/data/*.db
sudo systemctl restart solana-ai-trader
```

### Out of memory

1. **Add swap space:**
```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

2. **Reduce worker count:**
Edit systemd service file:
```ini
ExecStart=/home/trader/venv/bin/uvicorn src.api:app --workers 2
```

### High CPU usage

1. **Check process:**
```bash
sudo htop
```

2. **Reduce API call frequency**
3. **Optimize LLM model selection** (use Claude Haiku)

---

## Performance Tuning

### Uvicorn Workers

Adjust worker count based on CPU cores:

```bash
# For 4 CPU cores
ExecStart=... --workers 4

# For 2 CPU cores
ExecStart=... --workers 2
```

### Database Optimization

1. **Regular cleanup:**
```bash
# Old trades cleanup (keep last 1000)
sqlite3 data/trading.db "DELETE FROM trades WHERE id NOT IN (SELECT id FROM trades ORDER BY timestamp DESC LIMIT 1000);"
```

2. **Vacuum database:**
```bash
sqlite3 data/trading.db "VACUUM;"
```

---

## Production Checklist

Before going live:

- [ ] Environment set to `production`
- [ ] Wallet private key configured securely
- [ ] LLM API key configured
- [ ] Telegram/Discord notifications tested
- [ ] Risk management limits set appropriately
- [ ] SSL/TLS certificate installed
- [ ] Firewall configured
- [ ] Backup strategy in place
- [ ] Monitoring configured
- [ ] Logs rotation configured
- [ ] Started with small test amounts
- [ ] Verified paper trading mode works

---

## Support

For issues or questions:

- Check logs: `journalctl -u solana-ai-trader -f`
- Review configuration: Check `.env` file
- Test connectivity: Verify RPC endpoints
- Check documentation: See README.md

## Disclaimer

This software is provided for educational purposes. Cryptocurrency trading involves substantial risk. Always test thoroughly and start with small amounts.
