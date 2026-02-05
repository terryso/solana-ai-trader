from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class LLMResponse:
  """Response from LLM."""
  content: str
  model: str
  tokens_used: int = 0
  finish_reason: str = ''


@dataclass
class TradingAnalysis:
  """Trading analysis result from LLM."""
  action: str  # buy, sell, hold
  strength: str  # very_weak, weak, moderate, strong, very_strong
  confidence: float  # 0.0 to 1.0
  risk_level: str  # low, medium, high
  reasoning: str
  entry_price: Optional[float] = None
  stop_loss: Optional[float] = None
  take_profit: Optional[float] = None
  position_size_percent: Optional[float] = None  # Recommended position size %


class BaseLLMClient(ABC):
  """Base class for LLM clients."""

  def __init__(self, api_key: str, model: str):
    """
    Initialize LLM client.

    Args:
        api_key: API key for the service
        model: Model name
    """
    self.api_key = api_key
    self.model = model

  @abstractmethod
  async def generate(
    self,
    prompt: str,
    max_tokens: int = 1000,
    temperature: float = 0.7
  ) -> LLMResponse:
    """
    Generate text from prompt.

    Args:
        prompt: Input prompt
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature (0-1)

    Returns:
        LLMResponse
    """
    pass

  @abstractmethod
  async def generate_json(
    self,
    prompt: str,
    schema: Dict[str, Any],
    max_tokens: int = 1000,
    temperature: float = 0.7
  ) -> Dict[str, Any]:
    """
    Generate JSON output from prompt.

    Args:
        prompt: Input prompt
        schema: Expected JSON schema
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature

    Returns:
        JSON object
    """
    pass

  @abstractmethod
  async def analyze_trading_signal(
    self,
    market_data: Dict[str, Any],
    technical_indicators: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
  ) -> TradingAnalysis:
    """
    Analyze market and generate trading signal.

    Args:
        market_data: Market data (price, volume, etc.)
        technical_indicators: Technical indicators
        context: Additional context (news, sentiment, etc.)

    Returns:
        TradingAnalysis
    """
    pass
