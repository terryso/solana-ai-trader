from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from pathlib import Path

from src.config import settings

# Create data directory if it doesn't exist
data_dir = Path(settings.database_url.replace('sqlite:///', ''))
data_dir.parent.mkdir(parents=True, exist_ok=True)

# Create engine
engine = create_engine(
  settings.database_url,
  connect_args={'check_same_thread': False} if 'sqlite' in settings.database_url else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


class TradeRecord(Base):
  """Trade record table."""
  __tablename__ = 'trades'

  id = Column(Integer, primary_key=True, index=True)
  trade_type = Column(String, nullable=False)  # buy/sell
  token_address = Column(String, nullable=False, index=True)
  token_symbol = Column(String, nullable=False)
  amount = Column(Float, nullable=False)
  price = Column(Float, nullable=False)
  value_usd = Column(Float, nullable=False)
  status = Column(String, nullable=False, default='pending')
  signature = Column(String, unique=True, nullable=True)
  signal_id = Column(Integer, nullable=True)
  timestamp = Column(DateTime, default=datetime.utcnow)
  executed_at = Column(DateTime, nullable=True)
  error_message = Column(Text, nullable=True)


class SignalRecord(Base):
  """Signal record table."""
  __tablename__ = 'signals'

  id = Column(Integer, primary_key=True, index=True)
  token_address = Column(String, nullable=False, index=True)
  token_symbol = Column(String, nullable=False)
  action = Column(String, nullable=False)  # buy/sell/hold
  strength = Column(String, nullable=False)
  confidence = Column(Float, nullable=False)
  risk_level = Column(String, nullable=False)
  reasoning = Column(Text, nullable=False)
  entry_price = Column(Float, nullable=True)
  stop_loss = Column(Float, nullable=True)
  take_profit = Column(Float, nullable=True)
  timestamp = Column(DateTime, default=datetime.utcnow)
  executed = Column(Integer, default=0)  # 0=no, 1=yes


class MarketDataRecord(Base):
  """Market data history table."""
  __tablename__ = 'market_data'

  id = Column(Integer, primary_key=True, index=True)
  token_address = Column(String, nullable=False, index=True)
  token_symbol = Column(String, nullable=False)
  price = Column(Float, nullable=False)
  volume_24h = Column(Float, nullable=False)
  price_change_24h = Column(Float, nullable=False)
  market_cap = Column(Float, nullable=True)
  liquidity_usd = Column(Float, nullable=True)
  timestamp = Column(DateTime, default=datetime.utcnow, index=True)


def init_db():
  """Initialize database tables."""
  Base.metadata.create_all(bind=engine)


def get_db():
  """Get database session."""
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()
