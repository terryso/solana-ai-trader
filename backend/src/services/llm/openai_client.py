import json
import openai
from typing import Dict, Any, Optional, List

from src.config import settings
from src.utils import logger, async_retry
from .base import BaseLLMClient, LLMResponse, TradingAnalysis


class OpenAIClient(BaseLLMClient):
  """OpenAI API client (fallback option)."""

  def __init__(
    self,
    api_key: Optional[str] = None,
    model: Optional[str] = None
  ):
    """
    Initialize OpenAI client.

    Args:
        api_key: OpenAI API key (defaults to settings)
        model: Model name (defaults to settings)
    """
    api_key = api_key or settings.openai_api_key
    model = model or settings.llm_model

    super().__init__(api_key, model)

    self.client = openai.AsyncOpenAI(api_key=api_key)

  @async_retry(max_retries=3, delay=1.0)
  async def generate(
    self,
    prompt: str,
    max_tokens: int = 1000,
    temperature: float = 0.7
  ) -> LLMResponse:
    """
    Generate text from prompt using OpenAI.

    Args:
        prompt: Input prompt
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature

    Returns:
        LLMResponse
    """
    try:
      response = await self.client.chat.completions.create(
        model=self.model,
        messages=[{'role': 'user', 'content': prompt}],
        max_tokens=max_tokens,
        temperature=temperature
      )

      message = response.choices[0].message
      tokens_used = response.usage.total_tokens

      return LLMResponse(
        content=message.content,
        model=self.model,
        tokens_used=tokens_used,
        finish_reason=response.choices[0].finish_reason
      )

    except Exception as e:
      logger.error(f'Error generating text with OpenAI: {e}')
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
    Generate JSON output from prompt using OpenAI.

    Args:
        prompt: Input prompt
        schema: Expected JSON schema
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature

    Returns:
        JSON object
    """
    try:
      # Use JSON mode if available (GPT-4 and newer)
      json_prompt = f'''{prompt}

IMPORTANT: Respond ONLY with a valid JSON object following this schema:

```json
{json.dumps(schema, indent=2)}
```
'''

      response = await self.client.chat.completions.create(
        model=self.model,
        messages=[{'role': 'user', 'content': json_prompt}],
        max_tokens=max_tokens,
        temperature=temperature,
        response_format={'type': 'json_object'}  # Enable JSON mode
      )

      content = response.choices[0].message.content
      return json.loads(content)

    except Exception as e:
      logger.error(f'Error generating JSON with OpenAI: {e}')
      raise

  async def analyze_trading_signal(
    self,
    market_data: Dict[str, Any],
    technical_indicators: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
  ) -> TradingAnalysis:
    """
    Analyze market and generate trading signal using OpenAI.

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
