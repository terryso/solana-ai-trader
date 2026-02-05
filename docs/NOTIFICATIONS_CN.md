# 通知设置指南

本指南说明如何为Solana AI Trader设置Telegram和Discord通知。

[English](NOTIFICATIONS.md) | 简体中文

---

## 为什么使用通知？

即时获取以下情况的警报：
- ✅ 交易执行
- 📊 新交易信号生成
- 💼 投资组合更新
- 🚨 错误发生
- 📈 每日交易汇总

---

## Telegram设置

### 第1步：创建Telegram机器人

1. 打开Telegram，搜索[@BotFather](https://t.me/BotFather)
2. 发送`/newbot`命令
3. 按提示命名机器人（例如"My Trading Bot"）
4. 复制机器人令牌（格式：`123456789:ABCdefGHIjklMNOpqrsTUVwxyz`）

### 第2步：获取聊天ID

1. 搜索[@userinfobot](https://t.me/userinfobot)
2. 发送`/start`命令
3. 复制聊天ID（格式：`123456789`）

### 第3步：配置环境变量

编辑`.env`文件：

```bash
# Telegram配置
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

### 第4步：测试连接

```bash
cd backend
python examples/notifications_example.py
```

你应该在Telegram收到测试消息！

---

## Discord设置

### 第1步：创建Discord Webhook

1. 打开Discord服务器
2. 进入**服务器设置** → **集成**
3. 点击**Webhooks** → **新建Webhook**
4. 命名为"Solana AI Trader"
5. 选择发布到的频道
6. 复制webhook URL

### 第2步：配置环境变量

编辑`.env`文件：

```bash
# Discord配置
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/123456789/ABCdefGHIjklMNOpqrsTUVwxyz
```

### 第3步：测试连接

```bash
cd backend
python examples/notifications_example.py
```

你应该在Discord收到测试消息！

---

## 通知类型

### 交易通知
交易执行时发送：
```
🟢 交易 ✅

类型: 买入
代币: SOL
数量: 10.500000
价格: $145.50
价值: $1,527.75
状态: 已执行

交易: abc123...xyz789
```

### 信号通知
LLM生成新交易信号时发送：
```
🟢 新交易信号

操作: 买入
代币: BONK
强度: 强
置信度: 85%
风险: 中等

分析: RSI显示超卖条件...
```

### 投资组合更新
```
💼 投资组合更新

总价值: $5,432.10
未实现盈亏: 📈 +$234.50 (+4.51%)
持仓数量: 3
```

### 每日汇总
```
📊 每日交易汇总

总交易: 15
总买入: $3,200.00
总卖出: $3,434.50
净盈亏: 📈 +$234.50
```

---

## 高级配置

### 静默通知

发送无声音的通知：

```python
await telegram.send_message(
    text='静默更新',
    disable_notification=True
)
```

### 自定义消息

```python
from src.services.notifications import get_telegram_notifier

telegram = get_telegram_notifier()
await telegram.send_message(
    text='<b>自定义消息</b> 带<i>格式</i>',
    parse_mode='HTML'
)
```

### Discord Embeds

```python
from src.services.notifications import get_discord_notifier

discord = get_discord_notifier()
await discord.send_message(
    embeds=[{
        'title': '自定义Embed',
        'description': '带自定义字段',
        'color': 0x00ff00,
        'fields': [
            {'name': '字段1', 'value': '值1'},
            {'name': '字段2', 'value': '值2'}
        ]
    }]
)
```

---

## 最佳实践

1. **同时使用Telegram和Discord**以实现冗余
2. **测试通知**后再部署到生产环境
3. **保持聊天ID安全** - 永不提交到git
4. **使用专用频道**进行交易警报
5. **在Discord中设置通知过滤**（如需要）

## 故障排除

### Telegram: "Bad Token"错误
- 验证机器人令牌正确
- 检查机器人未被BotFather删除
- 确保令牌没有多余空格

### Telegram: "Chat Not Found"
- 验证聊天ID正确
- 先与机器人开始对话（发送/start）
- 检查机器人有权限向你发送消息

### Discord: Webhook不工作
- 验证webhook URL完整
- 检查webhook未被删除
- 确保机器人在频道有发布权限

### 未收到通知
- 检查`.env`文件是否正确加载
- 验证API密钥已设置
- 检查日志错误：`tail -f logs/trading.log`

## 安全提示

1. **绝不分享**你的机器人令牌或webhook URL
2. **使用环境变量** - 永不硬编码
3. **定期轮换**令牌（如需要）
4. **限制机器人权限**在Telegram
5. **使用专用webhook**用于每个环境

## 示例集成

通知系统自动集成到：

- **交易管理器**：交易执行后发送通知
- **信号服务**：新信号生成后发送通知
- **错误处理器**：发送关键错误警报

无需额外代码 - 只需配置凭据！

---

**关于设置的更多问题？** 查看[部署指南](DEPLOYMENT_CN.md)
