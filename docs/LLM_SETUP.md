# LLM Configuration Guide

Guide to configuring Solana AI Trader with various LLM providers, including Chinese domestic models.

English | **[简体中文](LLM_SETUP_CN.md)**

---

## Supported LLM Providers

### 1. Anthropic Claude (Recommended)

**Advantages:**
- Powerful analysis capabilities
- Excellent reasoning quality
- Long context support

**Configuration:**
```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_anthropic_key
LLM_MODEL=claude-3-5-sonnet-20241022
```

### 2. OpenAI GPT

**Configuration:**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_key
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4
```

### 3. Chinese Domestic Models (OpenAI-Compatible)

All Chinese domestic models compatible with OpenAI API protocol are supported!

#### DeepSeek

**Advantages:**
- Cost-effective
- Excellent performance
- Full OpenAI protocol compatibility

**Configuration:**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=your_deepseek_key
OPENAI_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```

**Get API Key:**
1. Visit https://platform.deepseek.com
2. Register account
3. Create API key

#### Moonshot (Kimi)

**Advantages:**
- Long context support
- Excellent Chinese understanding
- Stable and reliable

**Configuration:**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=your_moonshot_key
OPENAI_BASE_URL=https://api.moonshot.cn/v1
LLM_MODEL=moonshot-v1-8k
```

**Get API Key:**
1. Visit https://platform.moonshot.cn
2. Register account
3. Create API key

#### Qwen (Tongyi Qianwen)

**Advantages:**
- Alibaba Cloud
- Cost-effective
- Chinese optimized

**Configuration:**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=your_qwen_key
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-turbo
```

**Get API Key:**
1. Visit https://dashscope.aliyuncs.com
2. Login with Alibaba Cloud
3. Create API-KEY

#### Zhipu (ChatGLM)

**Advantages:**
- GLM series models
- Strong Chinese capabilities
- Multiple model choices

**Configuration:**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=your_zhipu_key
OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
LLM_MODEL=glm-4-flash
```

**Get API Key:**
1. Visit https://open.bigmodel.cn
2. Register/login
3. Create API key

#### Other Compatible Models

Any model supporting OpenAI API protocol:

```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=your_custom_base_url
LLM_MODEL=your_model_name
```

---

## Complete Configuration Examples

### Using DeepSeek (Recommended, Cost-Effective)

```bash
# .env file
ENVIRONMENT=paper_trading

# Use DeepSeek
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
OPENAI_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat

# Solana configuration
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
```

### Using Kimi

```bash
# .env file
ENVIRONMENT=paper_trading

# Use Kimi
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
OPENAI_BASE_URL=https://api.moonshot.cn/v1
LLM_MODEL=moonshot-v1-8k

# Solana configuration
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
```

### Using Claude (Original)

```bash
# .env file
ENVIRONMENT=paper_trading

# Use Claude
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
LLM_MODEL=claude-3-5-sonnet-20241022

# Solana configuration
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
```

---

## Testing Configuration

### Method 1: Run Example Script

```bash
cd backend
python examples/llm_analysis_example.py
```

### Method 2: Python Code Test

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

## Cost Comparison

| Provider | Model | Input Price | Output Price | Rating |
|----------|-------|-------------|--------------|--------|
| DeepSeek | deepseek-chat | ¥1/M tokens | ¥2/M tokens | ⭐⭐⭐⭐⭐ |
| Kimi | moonshot-v1-8k | ¥12/M tokens | ¥12/M tokens | ⭐⭐⭐⭐ |
| Qwen | qwen-turbo | ¥0.8/M tokens | ¥0.8/M tokens | ⭐⭐⭐⭐⭐ |
| Zhipu | glm-4-flash | ¥0.1/M tokens | ¥0.1/M tokens | ⭐⭐⭐⭐⭐ |
| Claude | claude-3-5-sonnet | $3/M tokens | $15/M tokens | ⭐⭐⭐⭐ |
| OpenAI | gpt-4 | $30/M tokens | $60/M tokens | ⭐⭐⭐ |

**Recommendation:** For budget-conscious users, use Qwen, Zhipu, or DeepSeek for excellent value!

---

## Troubleshooting

### Error: Authentication failed

**Problem:** Invalid API key

**Solution:**
```bash
# 1. Check API key
echo $OPENAI_API_KEY

# 2. Verify environment variable loaded
python -c "from src.config import settings; print(settings.openai_api_key)"

# 3. Recreate .env file
cp .env.example .env
# Fill in correct key
```

### Error: Connection failed

**Problem:** Incorrect BASE_URL

**Solution:**
```bash
# 1. Verify BASE_URL
curl -X POST https://api.deepseek.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"test"}]}'

# 2. Check network connection
ping api.deepseek.com

# 3. Confirm URL ends with /v1
# Correct: https://api.deepseek.com/v1
# Wrong: https://api.deepseek.com
```

### Error: Model not found

**Problem:** Incorrect model name

**Solution:**
```bash
# 1. Check model name spelling
# Correct: deepseek-chat
# Wrong: DeepSeek-Chat

# 2. Check provider documentation for available models
```

---

## Performance Optimization

### Use Faster Models

For real-time trading, response speed matters:

**Recommended (Balance speed and cost):**
```bash
LLM_PROVIDER=openai
OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
LLM_MODEL=glm-4-flash  # Fast and cheap
```

### Adjust Temperature

Adjust in code if needed:

```python
# More conservative analysis (low temperature)
response = await llm_client.generate(
    prompt=prompt,
    temperature=0.3  # 0-1, lower is more conservative
)

# More creative analysis (high temperature)
response = await llm_client.generate(
    prompt=prompt,
    temperature=0.8
)
```

---

## Best Practices

1. **Start with domestic models** - Low cost, high performance
2. **Use paper trading first** - Test configuration before real money
3. **Monitor API costs** - Set usage limits
4. **Backup configuration** - Multiple API keys for rate limiting
5. **Rotate keys regularly** - Security

---

## Support

For issues:
1. Check provider documentation
2. See [Troubleshooting](#troubleshooting) section
3. Check system logs: `tail -f logs/trading.log`

---

**Last Updated:** 2025-02-05
