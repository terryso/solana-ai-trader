# Solana AI Trader

由LLM分析驱动的Solana自动交易系统。

[English](README.md) | 简体中文

---

## 特性

- **AI驱动分析**：使用Claude/OpenAI进行智能交易决策
- **15+技术指标**：RSI、MACD、布林带等
- **自动交易**：基于AI信号24/7执行交易
- **风险管理**：可配置的限额保护资金
- **实时监控**：Web仪表板提供实时更新
- **通知推送**：Telegram/Discord即时通知
- **模拟交易**：无需真实资金即可测试策略

---

## 项目结构

```
solana-ai-trader/
├── backend/
│   ├── src/
│   │   ├── config/         # 配置管理
│   │   ├── database/       # 数据库模型和连接
│   │   ├── services/       # 核心服务（Solana、Jupiter、LLM）
│   │   ├── models/         # Pydantic模型
│   │   └── utils/          # 工具函数和日志
│   ├── logs/               # 应用日志
│   ├── data/               # 数据库文件
│   ├── requirements.txt
│   ├── .env.example
│   └── main.py
├── frontend/               # Web界面
├── deploy/                 # 部署脚本
├── docs/                   # 文档
└── README.md
```

---

## 快速开始

### 1. 安装

```bash
cd ~/solana-ai-trader
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 配置

```bash
cp .env.example .env
# 编辑.env文件，填入你的配置
```

### 3. 启动Web界面（推荐）

```bash
python run_server.py
```

然后访问：http://localhost:8000

Web仪表盘包含：
- 实时投资组合监控
- 交易历史
- 交易信号
- 自动刷新功能
- 响应式设计

### 4. CLI模式

#### 开发模式（测试）
```bash
python main.py
```

#### 模拟交易模式
```bash
# 在.env中设置 ENVIRONMENT=paper_trading
python main.py
```

#### 生产模式
```bash
# 在.env中设置 ENVIRONMENT=production
python main.py
```

---

## 风险管理

默认风险限制：
- 单笔最大仓位：投资组合的5%
- 每日损失限制：2%
- 止损：10%
- 最大持仓数：3个

**警告：** 先从模拟交易模式和小额资金开始！

---

## API使用示例

### 查询价格
```python
from src.services import get_market_data_client

client = get_market_data_client()
sol_price = await client.get_sol_price()
print(f'SOL价格: ${sol_price}')
```

### 执行交易
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

### 获取投资组合
```python
portfolio = await manager.get_portfolio_value()
print(f'总价值: ${portfolio.total_value_usd}')
print(f'盈亏: {portfolio.unrealized_pnl_percentage:.2f}%')
```

运行示例：
```bash
python examples/trading_example.py
python examples/llm_analysis_example.py
python examples/notifications_example.py
```

---

## 部署

### Docker（推荐）

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

### 手动部署

详见 [部署指南](docs/DEPLOYMENT_CN.md)，包含：
- 自动化安装脚本
- Systemd服务设置
- Nginx反向代理
- SSL/TLS配置
- 生产最佳实践

快速开始：
```bash
# 运行安装脚本
sudo bash deploy/install.sh

# 启动服务
sudo systemctl start solana-ai-trader

# 检查状态
sudo systemctl status solana-ai-trader
```

---

## 文档

- [用户手册](docs/USER_MANUAL_CN.md) - 完整使用指南
- [部署指南](docs/DEPLOYMENT_CN.md) - 部署文档
- [通知设置](docs/NOTIFICATIONS_CN.md) - Telegram/Discord设置

---

## 配置

编辑 `.env` 文件：

### 开发所需
- 无需API密钥即可进行基础测试

### 交易所需
- `SOLANA_WALLET_PRIVATE_KEY`：你的钱包私钥
- `ANTHROPIC_API_KEY` 或 `OPENAI_API_KEY`：LLM提供商密钥

### 可选但推荐
- `HELIUS_RPC_URL`：更好的Solana RPC性能
- `TELEGRAM_BOT_TOKEN`：交易通知

---

## 功能特性

### AI分析引擎
- ✅ Claude/OpenAI支持
- ✅ 15+技术指标
- ✅ 专业提示词工程
- ✅ 信号生成

### 交易执行
- ✅ Jupiter集成
- ✅ Solana区块链
- ✅ 钱包管理
- ✅ 交易历史

### 风险控制
- ✅ 仓位限制
- ✅ 止损止盈
- ✅ 每日损失限制
- ✅ 交易验证

### 监控界面
- ✅ 实时仪表盘
- ✅ 投资组合追踪
- ✅ 交易历史
- ✅ 信号监控

### 通知系统
- ✅ Telegram实时推送
- ✅ Discord Webhook
- ✅ 交易通知
- ✅ 每日汇总

---

## 路线图

- [x] 项目结构
- [x] 数据库模型
- [x] Solana RPC客户端
- [x] Jupiter集成
- [x] LLM分析引擎
- [x] 技术指标（15+个）
- [x] 交易信号生成
- [x] Web监控面板
- [x] Telegram/Discord通知
- [x] Docker部署
- [x] 生产部署脚本
- [ ] 回测系统
- [ ] 高级策略

---

## 技术栈

**后端：**
- Python 3.11
- FastAPI
- SQLAlchemy
- Solana.py
- Claude/OpenAI APIs

**前端：**
- 纯JavaScript
- HTML5/CSS3
- 响应式设计

**部署：**
- Docker
- Docker Compose
- Nginx
- Systemd

---

## 贡献

欢迎贡献！请随时提交Pull Request。

---

## 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## 免责声明

本软件仅供教育目的使用。加密货币交易涉及 substantial 的损失风险。使用风险自负。

---

## 致谢

使用 [Claude Code](https://claude.ai/code) 生成
via [Happy](https://happy.engineering)

Co-Authored-By: Claude <noreply@anthropic.com>
Co-Authored-By: Happy <yesreply@happy.engineering>
