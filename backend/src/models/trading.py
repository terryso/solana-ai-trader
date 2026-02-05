from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from enum import Enum


class TradeType(str, Enum):
  BUY = 'buy'
  SELL = 'sell'


class TradeStatus(str, Enum):
  PENDING = 'pending'
  EXECUTED = 'executed'
  FAILED = 'failed'
  CANCELLED = 'cancelled'


class SignalStrength(str, Enum):
  VERY_WEAK = 'very_weak'
  WEAK = 'weak'
  MODERATE = 'moderate'
  STRONG = 'strong'
  VERY_STRONG = 'very_strong'


class RiskLevel(str, Enum):
  LOW = 'low'
  MEDIUM = 'medium'
  HIGH = 'high'


class TokenInfo(BaseModel):
  """Token information."""
  address: str
  symbol: str
  name: str
  decimals: int


class TradingSignal(BaseModel):
  """LLM generated trading signal."""
  token_address: str
  token_symbol: str
  action: Literal['buy', 'sell', 'hold']
  strength: SignalStrength
  confidence: float = Field(ge=0, le=1)  # 0-1
  risk_level: RiskLevel
  reasoning: str
  entry_price: Optional[float] = None
  stop_loss: Optional[float] = None
  take_profit: Optional[float] = None
  timestamp: datetime = Field(default_factory=datetime.utcnow)


class Trade(BaseModel):
  """Trade record."""
  id: Optional[int] = None
  trade_type: TradeType
  token_address: str
  token_symbol: str
  amount: float
  price: float
  value_usd: float
  status: TradeStatus = TradeStatus.PENDING
  signature: Optional[str] = None
  signal_id: Optional[int] = None
  timestamp: datetime = Field(default_factory=datetime.utcnow)
  executed_at: Optional[datetime] = None
  error_message: Optional[str] = None


class Position(BaseModel):
  """Current position."""
  token_address: str
  token_symbol: str
  amount: float
  average_entry_price: float
  current_price: float
  value_usd: float
  pnl_usd: float
  pnl_percentage: float
  opened_at: datetime


class Portfolio(BaseModel):
  """Portfolio summary."""
  total_value_usd: float
  available_balance_sol: float
  positions: list[Position] = []
  unrealized_pnl_usd: float = 0
  unrealized_pnl_percentage: float = 0


class MarketData(BaseModel):
  """Market data for a token."""
  token_address: str
  token_symbol: str
  price: float
  volume_24h: float
  price_change_24h: float
  market_cap: Optional[float] = None
  liquidity_usd: Optional[float] = None
  timestamp: datetime = Field(default_factory=datetime.utcnow)
