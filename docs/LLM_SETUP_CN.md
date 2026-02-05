# LLM配置指南

本指南说明如何配置Solana AI Trader使用各种LLM提供商，包括国产大模型。

[English](LLM_SETUP.md) | 简体中文

---

## 支持的LLM提供商

### 1. Anthropic Claude（推荐）

**优势：**
- 强大的分析能力
- 优秀的推理质量
- 支持长上下文

**配置：**
```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_anthropic_key
LLM_MODEL=claude-3-5-sonnet-20241022
```

### 2. OpenAI GPT

**配置：**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_key
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4
```

### 3. 国产大模型（OpenAI兼容）

所有兼容OpenAI API协议的国产大模型都可以使用！

#### DeepSeek（深度求索）

**优势：**
- 价格实惠
- 性能优秀
- 完全兼容OpenAI协议

**配置：**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=your_deepseek_key
OPENAI_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```

**获取API密钥：**
1. 访问 https://platform.deepseek.com
2. 注册账号
3. 在API Keys页面创建密钥

#### Moonshot（Kimi）

**优势：**
- 长上下文支持
- 中文理解优秀
- 稳定可靠

**配置：**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=your_moonshot_key
OPENAI_BASE_URL=https://api.moonshot.cn/v1
LLM_MODEL=moonshot-v1-8k
```

**获取API密钥：**
1. 访问 https://platform.moonshot.cn
2. 注册账号
3. 创建API密钥

#### Qwen（通义千问）

**优势：**
- 阿里云出品
- 性价比高
- 中文优化

**配置：**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=your_qwen_key
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-turbo
```

**获取API密钥：**
1. 访问 https://dashscope.aliyuncs.com
2. 登录阿里云账号
3. 创建API-KEY

#### Zhipu（智谱AI）

**优势：**
- GLM系列模型
- 中文能力强
- 多种模型选择

**配置：**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=your_zhipu_key
OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
LLM_MODEL=glm-4-flash
```

**获取API密钥：**
1. 访问 https://open.bigmodel.cn
2. 注册/登录
3. 创建API密钥

#### 其他兼容模型

任何支持OpenAI API协议的模型都可以使用：

```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=your_custom_base_url
LLM_MODEL=your_model_name
```

---

## 完整配置示例

### 使用DeepSeek（推荐，性价比高）

```bash
# .env文件
ENVIRONMENT=paper_trading

# 使用DeepSeek
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
OPENAI_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat

# Solana配置
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
```

### 使用Kimi

```bash
# .env文件
ENVIRONMENT=paper_trading

# 使用Kimi
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
OPENAI_BASE_URL=https://api.moonshot.cn/v1
LLM_MODEL=moonshot-v1-8k

# Solana配置
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
```

### 使用Claude（原始配置）

```bash
# .env文件
ENVIRONMENT=paper_trading

# 使用Claude
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
LLM_MODEL=claude-3-5-sonnet-20241022

# Solana配置
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
```

---

## 测试配置

### 方法1：运行示例脚本

```bash
cd backend
python examples/llm_analysis_example.py
```

### 方法2：Python代码测试

```python
import asyncio
from src.services import get_signal_service

async def test():
    service = get_signal_service()
    signal = await service.generate_signal(
        token_address='So11111111111111111111111111111111111111112',
        token_symbol='SOL'
    )
    print(f"Action: {signal.action}")
    print(f"Reasoning: {signal.reasoning}")

asyncio.run(test())
```

---

## 成本对比

| 提供商 | 模型 | 输入价格 | 输出价格 | 推荐度 |
|--------|------|----------|----------|--------|
| DeepSeek | deepseek-chat | ¥1/百万tokens | ¥2/百万tokens | ⭐⭐⭐⭐⭐ |
| Kimi | moonshot-v1-8k | ¥12/百万tokens | ¥12/百万tokens | ⭐⭐⭐⭐ |
| Qwen | qwen-turbo | ¥0.8/百万tokens | ¥0.8/百万tokens | ⭐⭐⭐⭐⭐ |
| Zhipu | glm-4-flash | ¥0.1/百万tokens | ¥0.1/百万tokens | ⭐⭐⭐⭐⭐ |
| Claude | claude-3-5-sonnet | $3/百万tokens | $15/百万tokens | ⭐⭐⭐⭐ |
| OpenAI | gpt-4 | $30/百万tokens | $60/百万tokens | ⭐⭐⭐ |

**推荐：** 如果预算有限，使用Qwen、Zhipu或DeepSeek，性价比极高！

---

## 故障排除

### 错误：Authentication failed

**问题：** API密钥无效

**解决方案：**
```bash
# 1. 检查API密钥是否正确
echo $OPENAI_API_KEY

# 2. 确认环境变量已加载
python -c "from src.config import settings; print(settings.openai_api_key)"

# 3. 重新创建.env文件
cp .env.example .env
# 填入正确的密钥
```

### 错误：Connection failed

**问题：** BASE_URL配置错误

**解决方案：**
```bash
# 1. 验证BASE_URL
curl -X POST https://api.deepseek.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"test"}]}'

# 2. 检查网络连接
ping api.deepseek.com

# 3. 确认URL末尾是否有/v1
# 正确: https://api.deepseek.com/v1
# 错误: https://api.deepseek.com
```

### 错误：Model not found

**问题：** 模型名称错误

**解决方案：**
```bash
# 1. 检查模型名称拼写
# 正确: deepseek-chat
# 错误: DeepSeek-Chat

# 2. 查看提供商文档确认可用模型
```

---

## 性能优化

### 使用更快的模型

对于实时交易，响应速度很重要：

**推荐配置（平衡性能和成本）：**
```bash
LLM_PROVIDER=openai
OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
LLM_MODEL=glm-4-flash  # 快速且便宜
```

### 调整温度参数

在代码中调整（如需要）：

```python
# 更保守的分析（低温度）
response = await llm_client.generate(
    prompt=prompt,
    temperature=0.3  # 0-1之间，越低越保守
)

# 更有创意的分析（高温度）
response = await llm_client.generate(
    prompt=prompt,
    temperature=0.8
)
```

---

## 最佳实践

1. **从国产模型开始** - 成本低，性能好
2. **使用模拟交易测试** - 验证配置后再投入真实资金
3. **监控API调用成本** - 设置使用限额
4. **备用配置** - 配置多个API密钥以防限流
5. **定期更新密钥** - 安全考虑

---

## 支持

如有问题：
1. 查看提供商官方文档
2. 检查 [故障排除](#故障排除) 部分
3. 查看系统日志：`tail -f logs/trading.log`

---

**最后更新：** 2025-02-05
