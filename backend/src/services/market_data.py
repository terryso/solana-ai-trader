import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from decimal import Decimal

from src.config import settings
from src.utils import logger, async_retry
from src.models import MarketData


class MarketDataClient:
  """Client for fetching market data."""

  def __init__(self):
    """Initialize market data client."""
    self.client = httpx.AsyncClient(timeout=30.0)

  async def close(self):
    """Close HTTP client."""
    await self.client.aclose()

  @async_retry(max_retries=3, delay=1.0)
  async def get_token_price(
    self,
    token_mint: str,
    vs_token: str = 'usd'
  ) -> Optional[float]:
    """
    Get token price from Jupiter price API.

    Args:
        token_mint: Token mint address
        vs_token: Quote token (default: usd)

    Returns:
        Price in USD or None
    """
    try:
      response = await self.client.get(
        f'https://price.jup.ag/v6/price',
        params={'ids': token_mint}
      )
      response.raise_for_status()
      data = response.json()

      if token_mint in data and 'price' in data[token_mint]:
        return float(data[token_mint]['price'])

      return None
    except Exception as e:
      logger.error(f'Error fetching token price: {e}')
      return None

  async def get_multiple_prices(
    self,
    token_mints: List[str]
  ) -> Dict[str, float]:
    """
    Get prices for multiple tokens.

    Args:
        token_mints: List of token mint addresses

    Returns:
        Dictionary mapping mint addresses to prices
    """
    try:
      response = await self.client.get(
        'https://price.jup.ag/v6/price',
        params={'ids': ','.join(token_mints)}
      )
      response.raise_for_status()
      data = response.json()

      prices = {}
      for mint in token_mints:
        if mint in data and 'price' in data[mint]:
          prices[mint] = float(data[mint]['price'])

      return prices
    except Exception as e:
      logger.error(f'Error fetching multiple prices: {e}')
      return {}

  @async_retry(max_retries=3, delay=1.0)
  async def get_coin_gecko_price(
    self,
    coin_id: str,
    vs_currency: str = 'usd'
  ) -> Optional[float]:
    """
    Get price from CoinGecko (fallback).

    Args:
        coin_id: CoinGecko coin ID
        vs_currency: Quote currency

    Returns:
        Price or None
    """
    try:
      response = await self.client.get(
        f'https://api.coingecko.com/api/v3/simple/price',
        params={
          'ids': coin_id,
          'vs_currencies': vs_currency
        }
      )
      response.raise_for_status()
      data = response.json()

      if coin_id in data and vs_currency in data[coin_id]:
        return float(data[coin_id][vs_currency])

      return None
    except Exception as e:
      logger.error(f'Error fetching CoinGecko price: {e}')
      return None

  async def get_dex_screener_data(
    self,
    token_address: str
  ) -> Optional[Dict[str, Any]]:
    """
    Get token data from DexScreener.

    Args:
        token_address: Token address

    Returns:
        Token data or None
    """
    try:
      response = await self.client.get(
        f'https://api.dexscreener.com/latest/dex/tokens/{token_address}'
      )
      response.raise_for_status()
      data = response.json()

      if 'pairs' in data and len(data['pairs']) > 0:
        # Get the most liquid pair
        pairs = data['pairs']
        pairs.sort(key=lambda x: x.get('liquidity', {}).get('usd', 0), reverse=True)
        return pairs[0]

      return None
    except Exception as e:
      logger.error(f'Error fetching DexScreener data: {e}')
      return None

  async def get_comprehensive_market_data(
    self,
    token_address: str,
    token_symbol: str
  ) -> Optional[MarketData]:
    """
    Get comprehensive market data for a token.

    Args:
        token_address: Token mint address
        token_symbol: Token symbol

    Returns:
        MarketData object or None
    """
    try:
      # Get price from Jupiter
      price = await self.get_token_price(token_address)
      if price is None:
        return None

      # Try to get additional data from DexScreener
      volume_24h = 0.0
      price_change_24h = 0.0
      market_cap = None
      liquidity_usd = None

      dex_data = await self.get_dex_screener_data(token_address)
      if dex_data:
        volume_24h = dex_data.get('volume', {}).get('h24', 0.0)
        price_change_24h = dex_data.get('priceChange', {}).get('h24', 0.0)
        market_cap = dex_data.get('fdv', None)
        liquidity_usd = dex_data.get('liquidity', {}).get('usd', None)

      return MarketData(
        token_address=token_address,
        token_symbol=token_symbol,
        price=price,
        volume_24h=float(volume_24h),
        price_change_24h=float(price_change_24h),
        market_cap=float(market_cap) if market_cap else None,
        liquidity_usd=float(liquidity_usd) if liquidity_usd else None,
        timestamp=datetime.utcnow()
      )
    except Exception as e:
      logger.error(f'Error fetching comprehensive market data: {e}')
      return None

  async def get_sol_price(self) -> float:
    """
    Get current SOL price.

    Returns:
        SOL price in USD
    """
    from src.services.jupiter_client import SOL_MINT
    price = await self.get_token_price(SOL_MINT)
    return price if price else 0.0


# Global client instance
_market_data_client: Optional[MarketDataClient] = None


def get_market_data_client() -> MarketDataClient:
  """Get global market data client instance."""
  global _market_data_client
  if _market_data_client is None:
    _market_data_client = MarketDataClient()
  return _market_data_client
