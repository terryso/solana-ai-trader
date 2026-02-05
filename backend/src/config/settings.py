from pydantic_settings import BaseSettings
from typing import Literal
from functools import lru_cache


class Settings(BaseSettings):
  """Application settings loaded from environment variables."""

  # Solana Configuration
  solana_rpc_url: str
  solana_wallet_private_key: str = ''
  solana_network: str = 'mainnet-beta'
  helius_rpc_url: str = ''

  # Jupiter API
  jupiter_api_url: str = 'https://quote-api.jup.ag/v6'

  # LLM Configuration
  anthropic_api_key: str = ''
  openai_api_key: str = ''
  openai_base_url: str = 'https://api.openai.com/v1'  # Custom base URL for OpenAI-compatible APIs
  llm_provider: Literal['anthropic', 'openai'] = 'anthropic'
  llm_model: str = 'claude-3-5-sonnet-20241022'

  # Database
  database_url: str = 'sqlite:///./data/trading.db'
  supabase_url: str = ''
  supabase_key: str = ''

  # Redis
  redis_url: str = 'redis://localhost:6379'

  # Trading Configuration
  max_position_size: float = 0.05  # 5% of portfolio
  max_daily_loss: float = 0.02  # 2% daily loss limit
  stop_loss_percentage: float = 0.10  # 10% stop loss
  trade_slippage: float = 0.01  # 1% slippage

  # Risk Management
  max_open_positions: int = 3
  min_trade_amount_sol: float = 0.01
  reserve_balance_sol: float = 0.01

  # Logging
  log_level: str = 'INFO'
  log_file: str = 'logs/trading.log'

  # Notifications
  telegram_bot_token: str = ''
  telegram_chat_id: str = ''
  discord_webhook_url: str = ''

  # Environment
  environment: Literal['development', 'paper_trading', 'production'] = 'development'

  class Config:
    env_file = '.env'
    case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
  """Get cached settings instance."""
  return Settings()


# Global settings instance
settings = get_settings()
