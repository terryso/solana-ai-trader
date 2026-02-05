from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from src.config import settings
from src.utils import logger
from src.database import get_db, SignalRecord
from src.models import TradingSignal, MarketData
from src.services.market_data import get_market_data_client, MarketDataClient
from src.services.technical_indicators import analyze_price_history
from src.services.llm.base import BaseLLMClient
from src.services.llm.claude_client import ClaudeClient
from src.services.llm.openai_client import OpenAIClient
from src.services.notifications import get_telegram_notifier, get_discord_notifier


class SignalService:
  """Service for generating and managing trading signals."""

  def __init__(
    self,
    llm_client: Optional[BaseLLMClient] = None,
    market_client: Optional[MarketDataClient] = None
  ):
    """
    Initialize signal service.

    Args:
        llm_client: LLM client instance
        market_client: Market data client instance
    """
    self.llm_client = llm_client or self._create_llm_client()
    self.market_client = market_client or get_market_data_client()
    self.telegram = get_telegram_notifier()
    self.discord = get_discord_notifier()

  def _create_llm_client(self) -> BaseLLMClient:
    """
    Create LLM client based on settings.

    Returns:
        LLM client instance
    """
    if settings.llm_provider == 'anthropic' and settings.anthropic_api_key:
      return ClaudeClient()
    elif settings.llm_provider == 'openai' and settings.openai_api_key:
      return OpenAIClient()
    else:
      logger.warning('No LLM API key configured, using mock client')
      # Return a mock client for development
      return MockLLMClient()

  async def generate_signal(
    self,
    token_address: str,
    token_symbol: str,
    price_history: Optional[List[Dict[str, Any]]] = None,
    context: Optional[Dict[str, Any]] = None
  ) -> Optional[TradingSignal]:
    """
    Generate trading signal for a token.

    Args:
        token_address: Token mint address
        token_symbol: Token symbol
        price_history: Historical price data
        context: Additional context (news, sentiment, etc.)

    Returns:
        TradingSignal or None
    """
    try:
      # Get current market data
      market_data = await self.market_client.get_comprehensive_market_data(
        token_address=token_address,
        token_symbol=token_symbol
      )

      if not market_data:
        logger.error(f'Failed to get market data for {token_symbol}')
        return None

      # Calculate technical indicators
      technical_indicators = {}
      if price_history:
        technical_indicators = analyze_price_history(price_history)
      else:
        logger.warning(f'No price history provided for {token_symbol}, using basic analysis')

      # Prepare market data dict for LLM
      market_dict = {
        'token_symbol': market_data.token_symbol,
        'price': market_data.price,
        'volume_24h': market_data.volume_24h,
        'price_change_24h': market_data.price_change_24h,
        'market_cap': market_data.market_cap,
        'liquidity_usd': market_data.liquidity_usd,
      }

      # Generate signal using LLM
      analysis = await self.llm_client.analyze_trading_signal(
        market_data=market_dict,
        technical_indicators=technical_indicators,
        context=context or {}
      )

      # Create trading signal
      signal = TradingSignal(
        token_address=token_address,
        token_symbol=token_symbol,
        action=analysis.action,
        strength=analysis.strength,
        confidence=analysis.confidence,
        risk_level=analysis.risk_level,
        reasoning=analysis.reasoning,
        entry_price=analysis.entry_price,
        stop_loss=analysis.stop_loss,
        take_profit=analysis.take_profit,
        timestamp=datetime.utcnow()
      )

      # Save to database
      self._save_signal_to_db(signal, analysis)

      logger.info(
        f'Generated signal for {token_symbol}: {analysis.action.upper()} '
        f'(confidence: {analysis.confidence:.2f}, risk: {analysis.risk_level})'
      )

      # Send notifications
      if self.telegram.is_configured():
        await self.telegram.send_signal_notification(
          action=signal.action,
          token_symbol=token_symbol,
          strength=signal.strength,
          confidence=signal.confidence,
          risk_level=signal.risk_level,
          reasoning=signal.reasoning,
          entry_price=signal.entry_price
        )

      if self.discord.is_configured():
        await self.discord.send_signal_notification(
          action=signal.action,
          token_symbol=token_symbol,
          strength=signal.strength,
          confidence=signal.confidence,
          risk_level=signal.risk_level,
          reasoning=signal.reasoning,
          entry_price=signal.entry_price
        )

      return signal

    except Exception as e:
      logger.error(f'Error generating signal for {token_symbol}: {e}')
      return None

  def _save_signal_to_db(
    self,
    signal: TradingSignal,
    analysis: Any
  ) -> int:
    """
    Save signal to database.

    Args:
        signal: Trading signal
        analysis: LLM analysis result

    Returns:
        Signal ID
    """
    try:
      db: Session = next(get_db())
      record = SignalRecord(
        token_address=signal.token_address,
        token_symbol=signal.token_symbol,
        action=signal.action,
        strength=signal.strength,
        confidence=signal.confidence,
        risk_level=signal.risk_level,
        reasoning=signal.reasoning,
        entry_price=signal.entry_price,
        stop_loss=signal.stop_loss,
        take_profit=signal.take_profit,
        timestamp=signal.timestamp,
        executed=0
      )
      db.add(record)
      db.commit()
      db.refresh(record)
      return record.id
    except Exception as e:
      logger.error(f'Error saving signal to database: {e}')
      return 0

  def get_recent_signals(
    self,
    token_address: Optional[str] = None,
    limit: int = 50
  ) -> List[Dict[str, Any]]:
    """
    Get recent signals from database.

    Args:
        token_address: Filter by token address
        limit: Maximum number of signals

    Returns:
        List of signals
    """
    try:
      db: Session = next(get_db())
      query = db.query(SignalRecord)

      if token_address:
        query = query.filter(SignalRecord.token_address == token_address)

      signals = query.order_by(
        SignalRecord.timestamp.desc()
      ).limit(limit).all()

      return [
        {
          'id': s.id,
          'token_address': s.token_address,
          'token_symbol': s.token_symbol,
          'action': s.action,
          'strength': s.strength,
          'confidence': s.confidence,
          'risk_level': s.risk_level,
          'reasoning': s.reasoning,
          'entry_price': s.entry_price,
          'stop_loss': s.stop_loss,
          'take_profit': s.take_profit,
          'timestamp': s.timestamp,
          'executed': s.executed
        }
        for s in signals
      ]

    except Exception as e:
      logger.error(f'Error getting recent signals: {e}')
      return []

  def should_execute_signal(
    self,
    signal: TradingSignal
  ) -> tuple[bool, Optional[str]]:
    """
    Determine if a signal should be executed.

    Args:
        signal: Trading signal

    Returns:
        (should_execute, reason)
    """
    # Check confidence threshold
    if signal.confidence < 0.6:
      return False, f'Confidence too low: {signal.confidence:.2f}'

    # Check if action is hold
    if signal.action == 'hold':
      return False, 'Signal action is HOLD'

    # Check risk level
    if signal.risk_level == 'high' and settings.environment == 'production':
      return False, 'High risk signal in production mode'

    # Check signal strength
    if signal.strength in ['very_weak', 'weak']:
      return False, f'Signal strength too weak: {signal.strength}'

    return True, 'Signal meets execution criteria'


class MockLLMClient(BaseLLMClient):
  """Mock LLM client for development/testing."""

  def __init__(self):
    super().__init__('mock_api_key', 'mock_model')

  async def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7):
    from .base import LLMResponse
    return LLMResponse(
      content='Mock response',
      model='mock',
      tokens_used=0
    )

  async def generate_json(self, prompt: str, schema: Dict[str, Any], max_tokens: int = 1000, temperature: float = 0.7):
    return {
      'action': 'hold',
      'strength': 'moderate',
      'confidence': 0.5,
      'risk_level': 'medium',
      'reasoning': 'Mock LLM client - no real analysis',
      'entry_price': None,
      'stop_loss': None,
      'take_profit': None,
      'position_size_percent': None
    }

  async def analyze_trading_signal(self, market_data: Dict[str, Any], technical_indicators: Dict[str, Any], context: Optional[Dict[str, Any]] = None):
    from .base import TradingAnalysis
    return TradingAnalysis(
      action='hold',
      strength='moderate',
      confidence=0.5,
      risk_level='medium',
      reasoning='Mock LLM client - no real analysis. Configure ANTHROPIC_API_KEY or OPENAI_API_KEY for real signals.',
      entry_price=None,
      stop_loss=None,
      take_profit=None,
      position_size_percent=None
    )


# Global service instance
_signal_service: Optional[SignalService] = None


def get_signal_service() -> SignalService:
  """Get global signal service instance."""
  global _signal_service
  if _signal_service is None:
    _signal_service = SignalService()
  return _signal_service
