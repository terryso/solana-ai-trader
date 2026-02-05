import asyncio
from typing import Callable, Any, TypeVar
from functools import wraps
from datetime import datetime, timedelta

from src.utils.logger import logger

T = TypeVar('T')


def async_retry(max_retries: int = 3, delay: float = 1.0):
  """
  Async retry decorator.

  Args:
      max_retries: Maximum number of retries
      delay: Delay between retries in seconds
  """
  def decorator(func: Callable[..., T]) -> Callable[..., T]:
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
      last_exception = None
      for attempt in range(max_retries):
        try:
          return await func(*args, **kwargs)
        except Exception as e:
          last_exception = e
          if attempt < max_retries - 1:
            logger.warning(
              f'{func.__name__} failed (attempt {attempt + 1}/{max_retries}): {e}'
            )
            await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff
          else:
            logger.error(
              f'{func.__name__} failed after {max_retries} attempts: {e}'
            )
      raise last_exception
    return wrapper
  return decorator


def format_sol(amount: float, decimals: int = 6) -> str:
  """
  Format SOL amount with proper decimals.

  Args:
      amount: Amount in SOL
      decimals: Number of decimal places

  Returns:
      Formatted string
  """
  return f'{amount:.{decimals}f} SOL'


def format_usd(amount: float, decimals: int = 2) -> str:
  """
  Format USD amount with proper decimals.

  Args:
      amount: Amount in USD
      decimals: Number of decimal places

  Returns:
      Formatted string
  """
  return f'${amount:,.{decimals}f}'


def calculate_percentage_change(old_value: float, new_value: float) -> float:
  """
  Calculate percentage change.

  Args:
      old_value: Old value
      new_value: New value

  Returns:
      Percentage change
  """
  if old_value == 0:
    return 0.0
  return ((new_value - old_value) / old_value) * 100


def timestamp_to_datetime(timestamp: float) -> datetime:
  """
  Convert timestamp to datetime.

  Args:
      timestamp: Unix timestamp

  Returns:
      Datetime object
  """
  return datetime.fromtimestamp(timestamp)


def get_time_ago(delta: timedelta) -> str:
  """
  Get human-readable time ago string.

  Args:
      delta: Time difference

  Returns:
      Time ago string (e.g., "5 minutes ago")
  """
  seconds = int(delta.total_seconds())
  if seconds < 60:
    return f'{seconds} seconds ago'
  elif seconds < 3600:
    minutes = seconds // 60
    return f'{minutes} minute{"s" if minutes > 1 else ""} ago'
  elif seconds < 86400:
    hours = seconds // 3600
    return f'{hours} hour{"s" if hours > 1 else ""} ago'
  else:
    days = seconds // 86400
    return f'{days} day{"s" if days > 1 else ""} ago'


def truncate_address(address: str, start: int = 6, end: int = 4) -> str:
  """
  Truncate wallet/token address for display.

  Args:
      address: Full address
      start: Number of characters at start
      end: Number of characters at end

  Returns:
      Truncated address (e.g., "DVp7...1ZpK")
  """
  if len(address) <= start + end:
    return address
  return f'{address[:start]}...{address[-end:]}'


def validate_private_key(private_key: str) -> bool:
  """
  Validate private key format.

  Args:
      private_key: Private key string

  Returns:
      True if valid, False otherwise
  """
  # Basic validation - should be base58 or hex string
  if not private_key:
    return False
  try:
    # Check if it's reasonable length (64 bytes for ed25519 private key)
    if len(private_key) >= 64 and len(private_key) <= 128:
      return True
  except Exception:
    pass
  return False
