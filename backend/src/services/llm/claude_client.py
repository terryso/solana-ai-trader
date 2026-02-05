import json
import anthropic
from typing import Dict, Any, Optional, List

from src.config import settings
from src.utils import logger, async_retry
from .base import BaseLLMClient, LLMResponse, TradingAnalysis


class ClaudeClient(BaseLLMClient):
  """Claude API client."""

  def __init__(
    self,
    api_key: Optional[str] = None,
    model: Optional[str] = None
  ):
    """
    Initialize Claude client.

    Args:
        api_key: Anthropic API key (defaults to settings)
        model: Model name (defaults to settings)
    """
    api_key = api_key or settings.anthropic_api_key
    model = model or settings.llm_model

    super().__init__(api_key, model)

    self.client = anthropic.AsyncAnthropic(api_key=api_key)

  @async_retry(max_retries=3, delay=1.0)
  async def generate(
    self,
    prompt: str,
    max_tokens: int = 1000,
    temperature: float = 0.7
  ) -> LLMResponse:
    """
    Generate text from prompt using Claude.

    Args:
        prompt: Input prompt
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature

    Returns:
        LLMResponse
    """
    try:
      message = await self.client.messages.create(
        model=self.model,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[{'role': 'user', 'content': prompt}]
      )

      content = message.content[0].text
      tokens_used = message.usage.input_tokens + message.usage.output_tokens

      return LLMResponse(
        content=content,
        model=self.model,
        tokens_used=tokens_used,
        finish_reason=message.stop_reason
      )

    except Exception as e:
      logger.error(f'Error generating text with Claude: {e}')
      raise

  @async_retry(max_retries=3, delay=1.0)
  async def generate_json(
    self,
    prompt: str,
    schema: Dict[str, Any],
    max_tokens: int = 1000,
    temperature: float = 0.7
  ) -> Dict[str, Any]:
    """
    Generate JSON output from prompt using Claude.

    Args:
        prompt: Input prompt
        schema: Expected JSON schema
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature

    Returns:
        JSON object
    """
    try:
      # Add JSON formatting instruction to prompt
      json_prompt = f'''{prompt}

IMPORTANT: Respond ONLY with a valid JSON object. Do not include any explanatory text before or after the JSON.

Expected schema:
```json
{json.dumps(schema, indent=2)}
```
'''

      message = await self.client.messages.create(
        model=self.model,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[{'role': 'user', 'content': json_prompt}]
      )

      content = message.content[0].text

      # Parse JSON response
      # Handle case where model wraps JSON in markdown code blocks
      if content.startswith('```'):
        content = content.split('```')[1]
        if content.startswith('json'):
          content = content[4:]

      return json.loads(content.strip())

    except Exception as e:
      logger.error(f'Error generating JSON with Claude: {e}')
      raise

  async def analyze_trading_signal(
    self,
    market_data: Dict[str, Any],
    technical_indicators: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
  ) -> TradingAnalysis:
    """
    Analyze market and generate trading signal using Claude.

    Args:
        market_data: Market data (price, volume, etc.)
        technical_indicators: Technical indicators
        context: Additional context (news, sentiment, etc.)

    Returns:
        TradingAnalysis
    """
    from .prompts import TRADING_ANALYSIS_PROMPT

    # Build analysis prompt
    prompt = TRADING_ANALYSIS_PROMPT.format(
      token_symbol=market_data.get('token_symbol', 'UNKNOWN'),
      current_price=market_data.get('price', 0),
      volume_24h=market_data.get('volume_24h', 0),
      price_change_24h=market_data.get('price_change_24h', 0),
      market_cap=market_data.get('market_cap', 'N/A'),
      liquidity=market_data.get('liquidity_usd', 'N/A'),
      technical_indicators=json.dumps(technical_indicators, indent=2),
      additional_context=json.dumps(context or {}, indent=2)
    )

    # Define expected schema
    schema = {
      'action': 'buy | sell | hold',
      'strength': 'very_weak | weak | moderate | strong | very_strong',
      'confidence': 'float (0.0 to 1.0)',
      'risk_level': 'low | medium | high',
      'reasoning': 'string (explain your analysis)',
      'entry_price': 'float or null',
      'stop_loss': 'float or null',
      'take_profit': 'float or null',
      'position_size_percent': 'float or null (recommended position size as % of portfolio)'
    }

    # Generate analysis
    response = await self.generate_json(
      prompt=prompt,
      schema=schema,
      max_tokens=1500,
      temperature=0.3  # Lower temperature for more consistent analysis
    )

    return TradingAnalysis(
      action=response['action'],
      strength=response['strength'],
      confidence=float(response['confidence']),
      risk_level=response['risk_level'],
      reasoning=response['reasoning'],
      entry_price=response.get('entry_price'),
      stop_loss=response.get('stop_loss'),
      take_profit=response.get('take_profit'),
      position_size_percent=response.get('position_size_percent')
    )
