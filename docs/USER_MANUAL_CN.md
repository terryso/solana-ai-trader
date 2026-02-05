# Solana AI Trader - 用户手册

[English](../USER_MANUAL.md) | 简体中文

完整的Solana AI Trader系统使用指南。

---

## 目录

1. [简介](#简介)
2. [快速开始](#快速开始)
3. [配置说明](#配置说明)
4. [使用Web仪表盘](#使用web仪表盘)
5. [交易策略](#交易策略)
6. [风险管理](#风险管理)
7. [通知设置](#通知设置)
8. [API参考](#api参考)
9. [故障排除](#故障排除)
10. [最佳实践](#最佳实践)

---

## 简介

### 什么是Solana AI Trader？

Solana AI Trader是一个自动交易系统，具有以下特点：
- 使用大语言模型（LLM）分析市场状况
- 通过Jupiter在Solana区块链上执行交易
- 提供Web实时监控仪表盘
- 发送Telegram/Discord通知
- 实施全面的风险管理

### 核心功能

- **AI驱动分析**：利用Claude/OpenAI进行智能交易决策
- **15+技术指标**：RSI、MACD、布林带等
- **自动交易**：基于AI信号全天候执行交易
- **风险管理**：可配置的限额保护资本
- **实时监控**：Web仪表盘提供实时更新
- **通知推送**：即时交易和信号警报
- **模拟交易**：无需真实资金即可测试策略

---

## 快速开始

### 安装（5分钟）

1. **安装依赖：**
```bash
sudo apt-get install python3.11 python3.11-venv git
```

2. **克隆并设置：**
```bash
cd ~
git clone <repository_url> solana-ai-trader
cd solana-ai-trader/backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **配置：**
```bash
cp .env.example .env
nano .env
```

最简配置：
```bash
ENVIRONMENT=paper_trading  # 从模拟交易开始
ANTHROPIC_API_KEY=your_key_here  # 用于LLM分析
```

4. **启动：**
```bash
python run_server.py
```

5. **访问仪表盘：**
```
http://localhost:8000
```

### 第一次交易

1. **生成信号：**
```python
from src.services import get_signal_service
import asyncio

async def get_signal():
    service = get_signal_service()
    signal = await service.generate_signal(
        token_address='So11111111111111111111111111111111111111112',
        token_symbol='SOL',
        price_history=[]
    )
    print(f"操作: {signal.action}")
    print(f"置信度: {signal.confidence}")
    print(f"分析: {signal.reasoning}")

asyncio.run(get_signal())
```

2. **执行交易**（如果信号良好）：
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
    print(f"交易已执行: {trade}")

asyncio.run(execute_trade())
```

---

## 配置说明

### 环境变量

在`backend`目录创建`.env`文件：

#### 基本设置

```bash
# 环境
ENVIRONMENT=development  # development | paper_trading | production

# Solana配置
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
HELIUS_RPC_URL=  # 可选但推荐

# 钱包（仅生产环境）
SOLANA_WALLET_PRIVATE_KEY=  # 你的钱包私钥

# LLM配置
ANTHROPIC_API_KEY=  # Claude
OPENAI_API_KEY=  # GPT（备选）
LLM_PROVIDER=anthropic  # anthropic | openai
LLM_MODEL=claude-3-5-sonnet-20241022
```

#### 风险管理

```bash
# 仓位大小
MAX_POSITION_SIZE=0.05  # 每笔交易最大5%
MAX_OPEN_POSITIONS=3    # 最大并发持仓数
MIN_TRADE_AMOUNT_SOL=0.01  # 最小交易量

# 止损和限制
STOP_LOSS_PERCENTAGE=0.10  # 10%止损
MAX_DAILY_LOSS=0.02  # 每日2%损失限制后停止

# 交易参数
TRADE_SLIPPAGE=0.01  # 1%滑点容忍度
RESERVE_BALANCE_SOL=0.01  # 保留0.01 SOL作为手续费
```

#### 通知

```bash
# Telegram
TELEGRAM_BOT_TOKEN=  # 从@BotFather获取
TELEGRAM_CHAT_ID=  # 从@userinfobot获取

# Discord
DISCORD_WEBHOOK_URL=  # 从服务器设置获取
```

### 推荐配置

#### 测试/开发
```bash
ENVIRONMENT=development
LLM_PROVIDER=anthropic
# 无需钱包
```

#### 模拟交易
```bash
ENVIRONMENT=paper_trading
LLM_PROVIDER=anthropic
# 模拟交易，无真实资金
```

#### 生产（小额账户）
```bash
ENVIRONMENT=production
MAX_POSITION_SIZE=0.02  # 每笔2%
MAX_DAILY_LOSS=0.01  # 每日1%限制
MAX_OPEN_POSITIONS=2
MIN_TRADE_AMOUNT_SOL=0.05
STOP_LOSS_PERCENTAGE=0.08
```

---

## 使用Web仪表盘

### 访问仪表盘

1. **启动服务器：**
```bash
cd backend
python run_server.py
```

2. **打开浏览器：**
```
http://localhost:8000
```

### 仪表盘部分

#### 1. 统计卡片

顶部显示4个关键指标：
- **投资组合价值**：总价值（美元）
- **可用余额**：可用于交易的SOL
- **每日盈亏**：今天的盈亏
- **今日信号**：生成的信号数量

颜色编码：
- 🟢 绿色：盈利
- 🔴 红色：亏损
- ⚪ 灰色：中性

#### 2. 投资组合标签

显示当前持仓：
- 代币符号和数量
- 入场价 vs 当前价
- 未实现盈亏（金额和百分比）
- 持仓时间

#### 3. 交易历史标签

列出所有已执行交易：
- 时间戳
- 类型（买入/卖出）
- 代币
- 数量
- 价格
- 价值（美元）
- 状态（待定/已执行/失败）

#### 4. 信号标签

显示AI生成的交易信号：
- 时间戳
- 操作（买入/卖出/持有）
- 信号强度
- 置信度
- 风险评估
- LLM分析理由

### 自动刷新

配置自动数据刷新：
- 关闭：仅手动刷新
- 5秒：实时监控
- 15秒：平衡（默认）
- 30秒：减少API调用
- 1分钟：最小更新

---

## 交易策略

### 内置策略：AI信号跟随

系统使用LLM分析基于以下内容生成信号：
- 技术指标（RSI、MACD等）
- 价格走势模式
- 成交量分析
- 市场状况

### 策略工作流程

1. **数据收集** - 获取当前价格、24h成交量、计算技术指标
2. **LLM分析** - 发送数据到Claude/GPT，获取交易建议
3. **信号评估** - 检查置信度（>60%）、风险等级、信号强度
4. **交易执行** - 计算仓位、验证风险限制、通过Jupiter执行

### 自定义策略示例

```python
async def custom_strategy():
    """自定义策略：仅交易强信号"""

    signal_service = get_signal_service()
    trading_manager = get_trading_manager()

    signal = await signal_service.generate_signal(
        token_address='So11111111111111111111111111111111111111112',
        token_symbol='SOL'
    )

    # 自定义标准
    if (signal.action == 'buy' and
        signal.confidence > 0.75 and
        signal.strength in ['strong', 'very_strong'] and
        signal.risk_level != 'high'):

        # 计算仓位（高置信度时更激进）
        base_amount = 1.0  # SOL
        multiplier = 1 + (signal.confidence - 0.75)
        amount = base_amount * multiplier

        trade = await trading_manager.execute_trade_with_validation(
            token_mint=signal.token_address,
            token_symbol=signal.token_symbol,
            amount_sol=amount,
            trade_type=TradeType.BUY
        )
```

---

## 风险管理

### 内置风控

#### 1. 仓位限制
```bash
MAX_POSITION_SIZE=0.05  # 投资组合的5%
```

#### 2. 每日损失限制
```bash
MAX_DAILY_LOSS=0.02  # 每日2%
```

#### 3. 止损
```bash
STOP_LOSS_PERCENTAGE=0.10  # 10%止损
```

#### 4. 持仓限制
```bash
MAX_OPEN_POSITIONS=3  # 最大3个并发持仓
```

### 自定义风险管理

```python
async def safe_trade():
    trading_manager = get_trading_manager()

    # 检查每日损失
    if trading_manager.should_stop_trading():
        print("已达到每日损失限制，停止交易")
        return

    # 获取投资组合
    portfolio = await trading_manager.get_portfolio_value()

    # 检查可用余额
    if portfolio.available_balance_sol < 0.1:
        print("余额不足")
        return

    # 检查持仓数量
    if len(portfolio.positions) >= 3:
        print("持仓过多")
        return

    # 执行交易
    trade = await trading_manager.execute_trade_with_validation(...)
```

---

## 通知设置

### 设置Telegram

1. **创建机器人：**
   - 打开Telegram，搜索@BotFather
   - 发送`/newbot`
   - 按说明操作
   - 复制机器人令牌

2. **获取聊天ID：**
   - 搜索@userinfobot
   - 发送`/start`
   - 复制聊天ID

3. **配置：**
```bash
TELEGRAM_BOT_TOKEN=你的令牌
TELEGRAM_CHAT_ID=你的聊天ID
```

4. **测试：**
```python
from src.services.notifications import get_telegram_notifier
import asyncio

asyncio.run(get_telegram_notifier().test_connection())
```

### 设置Discord

1. **创建Webhook：**
   - 服务器设置 → 集成
   - Webhooks → 新建Webhook
   - 复制webhook URL

2. **配置：**
```bash
DISCORD_WEBHOOK_URL=你的webhook_url
```

---

## API参考

### Trading Manager

#### 获取投资组合
```python
manager = get_trading_manager()
portfolio = await manager.get_portfolio_value()
```

#### 执行交易
```python
trade = await manager.execute_trade_with_validation(
    token_mint='EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
    token_symbol='USDC',
    amount_sol=1.0,
    trade_type=TradeType.BUY
)
```

### Signal Service

#### 生成信号
```python
service = get_signal_service()
signal = await service.generate_signal(
    token_address='So11111111111111111111111111111111111111112',
    token_symbol='SOL'
)
```

### REST API端点

```
GET /api/portfolio      # 获取投资组合
GET /api/trades         # 获取交易历史
GET /api/signals        # 获取信号
GET /api/stats          # 获取统计
GET /api/health         # 健康检查
```

---

## 故障排除

### 常见问题

#### 服务无法启动
```bash
# 检查日志
sudo journalctl -u solana-ai-trader -n 50

# 检查端口
sudo netstat -tlnp | grep 8000

# 验证Python版本
python --version  # 应该是3.11+
```

#### 模块未找到错误
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

#### 数据库锁定
```bash
# 停止服务
sudo systemctl stop solana-ai-trader

# 移除锁文件
rm backend/data/*.db-journal

# 重启
sudo systemctl start solana-ai-trader
```

---

## 最佳实践

### 1. 从小开始
- 始终从模拟交易开始
- 生产中使用小额资金
- 逐步增加投入

### 2. 定期监控
- 每日查看仪表盘
- 验证信号质量
- 监控盈亏

### 3. 风险管理
- 保守设置
- 分散投资
- 保留部分SOL作为手续费

### 4. 维护
- 定期更新代码
- 备份数据库
- 清理旧数据

---

## 支持

### 文档

- [README](../README_CN.md) - 项目概述
- [部署指南](DEPLOYMENT_CN.md) - 部署说明
- [通知设置](NOTIFICATIONS_CN.md) - 通知设置

### 示例

- `examples/trading_example.py` - 交易示例
- `examples/llm_analysis_example.py` - LLM分析
- `examples/notifications_example.py` - 通知测试

### 免责声明

本软件仅供教育目的使用。加密货币交易涉及 substantial 的损失风险。

**重要提示：**
- 始终从模拟交易开始
- 永远不要投入超过你承受能力的资金
- 使用真实资金前了解风险
- 过往表现不保证未来结果

**你完全对自己的交易决策和结果负责。**

---

**最后更新：** 2025-02-05

**如需最新更新和文档，请访问GitHub仓库。**
