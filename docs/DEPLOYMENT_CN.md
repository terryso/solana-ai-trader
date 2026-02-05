# 部署指南

本指南涵盖将Solana AI Trader部署到生产环境的完整流程。

[English](DEPLOYMENT.md) | 简体中文

---

## 目录

1. [快速开始（Docker）](#快速开始docker)
2. [手动部署](#手动部署)
3. [生产配置](#生产配置)
4. [SSL/TLS设置](#ssltls设置)
5. [监控和维护](#监控和维护)
6. [故障排除](#故障排除)

---

## 快速开始（Docker）

### 前置要求

- Docker Engine 20.10+
- Docker Compose 2.0+

### 步骤

1. **克隆仓库：**
```bash
git clone <repository_url>
cd solana-ai-trader
```

2. **配置环境：**
```bash
cp backend/.env.example backend/.env
nano backend/.env  # 编辑配置
```

3. **启动Docker Compose：**
```bash
docker-compose up -d
```

4. **查看日志：**
```bash
docker-compose logs -f solana-ai-trader
```

5. **访问仪表盘：**
```
http://localhost:8000
```

### 使用Nginx反向代理

```bash
docker-compose --profile with-nginx up -d
```

访问：`http://localhost`

---

## 手动部署

### 系统要求

- **操作系统：** Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- **Python：** 3.11+
- **内存：** 2GB最小，4GB推荐
- **存储：** 20GB最小
- **网络：** 稳定的互联网连接

### 自动化安装

1. **运行安装脚本：**
```bash
sudo bash deploy/install.sh
```

2. **编辑配置：**
```bash
sudo nano /home/trader/solana-ai-trader/backend/.env
```

3. **启动服务：**
```bash
sudo systemctl start solana-ai-trader
```

### 手动安装

1. **安装系统依赖：**

Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3-pip git nginx
```

CentOS/RHEL:
```bash
sudo yum install -y python311 python311-pip git nginx
```

2. **创建用户：**
```bash
sudo useradd -m -s /bin/bash trader
```

3. **设置应用：**
```bash
cd /home/trader/solana-ai-trader/backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. **配置环境：**
```bash
cp .env.example .env
nano .env
```

5. **设置systemd服务：**
```bash
sudo cp deploy/solana-ai-trader.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable solana-ai-trader
```

6. **启动服务：**
```bash
sudo systemctl start solana-ai-trader
```

---

## 生产配置

### 环境变量

编辑`.env`文件设置生产环境：

```bash
# 环境
ENVIRONMENT=production

# Solana RPC
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
HELIUS_RPC_URL=https://your-helius-rpc-url  # 推荐

# 钱包（绝不提交到git）
SOLANA_WALLET_PRIVATE_KEY=你的私钥

# LLM API
ANTHROPIC_API_KEY=你的anthropic密钥
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-sonnet-20241022

# 通知
TELEGRAM_BOT_TOKEN=你的机器人令牌
TELEGRAM_CHAT_ID=你的聊天ID

# 风险管理
MAX_POSITION_SIZE=0.05  # 每笔交易5%
MAX_DAILY_LOSS=0.02     # 每日2%损失限制
STOP_LOSS_PERCENTAGE=0.10
MAX_OPEN_POSITIONS=3
```

### 安全最佳实践

1. **文件权限：**
```bash
sudo chmod 600 /home/trader/solana-ai-trader/backend/.env
sudo chown trader:trader /home/trader/solana-ai-trader/backend/.env
```

2. **防火墙配置：**
```bash
# 允许HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 允许SSH
sudo ufw allow 22/tcp

# 启用防火墙
sudo ufw enable
```

3. **使用Helius RPC：**
- 更高的速率限制
- 更好的可靠性
- 更低的延迟

---

## SSL/TLS设置

### 使用Let's Encrypt（Certbot）

1. **安装Certbot：**
```bash
sudo apt-get install certbot python3-certbot-nginx
```

2. **获取证书：**
```bash
sudo certbot --nginx -d your-domain.com
```

3. **自动续期：**
```bash
sudo certbot renew --dry-run
```

---

## 监控和维护

### 检查服务状态

```bash
sudo systemctl status solana-ai-trader
```

### 查看日志

**实时日志：**
```bash
sudo journalctl -u solana-ai-trader -f
```

**应用日志：**
```bash
tail -f /home/trader/solana-ai-trader/logs/output.log
```

**Docker日志：**
```bash
docker-compose logs -f
```

### 重启服务

```bash
sudo systemctl restart solana-ai-trader
```

### 更新应用

**使用更新脚本：**
```bash
sudo bash deploy/update.sh
```

**手动更新：**
```bash
sudo systemctl stop solana-ai-trader
cd /home/trader/solana-ai-trader
git pull
cd backend
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl start solana-ai-trader
```

### 备份

**备份数据库和配置：**
```bash
tar -czf backup-$(date +%Y%m%d).tar.gz \
  /home/trader/solana-ai-trader/backend/data \
  /home/trader/solana-ai-trader/backend/.env
```

---

## 故障排除

### 服务无法启动

1. **检查日志：**
```bash
sudo journalctl -u solana-ai-trader -n 50
```

2. **验证配置：**
```bash
cd /home/trader/solana-ai-trader/backend
source venv/bin/activate
python -c "from src.config import settings; print(settings)"
```

3. **检查端口可用性：**
```bash
sudo netstat -tlnp | grep 8000
```

### 数据库错误

1. **检查数据库文件：**
```bash
ls -la /home/trader/solana-ai-trader/backend/data/
```

2. **重建数据库：**
```bash
rm /home/trader/solana-ai-trader/backend/data/*.db
sudo systemctl restart solana-ai-trader
```

### 内存不足

1. **添加交换空间：**
```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 生产检查清单

上线前检查：

- [ ] 环境设置为`production`
- [ ] 钱包私钥已配置
- [ ] LLM API密钥已配置
- [ ] Telegram/Discord通知已测试
- [ ] 风险管理限制已适当设置
- [ ] SSL/TLS证书已安装
- [ ] 防火墙已配置
- [ ] 备份策略已就位
- [ ] 监控已配置
- [ ] 日志轮换已配置
- [ ] 从小额测试开始
- [ ] 验证模拟交易模式工作

---

## 支持

如有问题或疑问：

- 检查日志：`journalctl -u solana-ai-trader -f`
- 查看配置：检查`.env`文件
- 测试连接：验证RPC端点
- 查看文档：参阅README.md

## 免责声明

本软件供教育目的使用。加密货币交易涉及 substantial 风险。始终彻底测试并从小额开始。
