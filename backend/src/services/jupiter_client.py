import httpx
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from decimal import Decimal

from src.config import settings
from src.utils import logger, async_retry


@dataclass
class PriceQuote:
  """Price quote from Jupiter."""
  input_mint: str
  output_mint: str
  input_amount: int
  output_amount: int
  price_impact_pct: float
  route_plan: List[Dict[str, Any]]


@dataclass
class SwapTransaction:
  """Prepared swap transaction."""
  swap_transaction: str  # Base64 encoded
  last_valid_block_height: int
  prioritization_fee_lamports: int


class JupiterClient:
  """Jupiter API client for Solana token swaps."""

  def __init__(self, api_url: Optional[str] = None):
    """
    Initialize Jupiter client.

    Args:
        api_url: Jupiter API URL. Defaults to Jupiter v6 API.
    """
    self.api_url = api_url or settings.jupiter_api_url
    self.client = httpx.AsyncClient(timeout=30.0)

  async def close(self):
    """Close HTTP client."""
    await self.client.aclose()

  @async_retry(max_retries=3, delay=1.0)
  async def get_token_list(self) -> List[Dict[str, Any]]:
    """
    Get list of supported tokens.

    Returns:
      List of token information
    """
    try:
      response = await self.client.get('https://token.jup.ag/all')
      response.raise_for_status()
      return response.json()
    except Exception as e:
      logger.error(f'Error fetching token list: {e}')
      return []

  @async_retry(max_retries=3, delay=1.0)
  async def get_price(
    self,
    input_mint: str,
    output_mint: str = 'So11111111111111111111111111111111111111112',  # Wrapped SOL
    amount: int = 1000000,
    slippage_bps: int = 50  # 0.5% slippage
  ) -> Optional[PriceQuote]:
    """
    Get price quote for token swap.

    Args:
        input_mint: Input token mint address
        output_mint: Output token mint address (default: WSOL)
        amount: Amount in smallest token units (lamports for SOL)
        slippage_bps: Slippage in basis points (100 = 1%)

    Returns:
        PriceQuote or None
    """
    try:
      params = {
        'inputMint': input_mint,
        'outputMint': output_mint,
        'amount': amount,
        'slippageBps': slippage_bps,
        'onlyDirectRoutes': False,
        'asLegacyTransaction': False,
      }

      response = await self.client.get(
        f'{self.api_url}/quote',
        params=params
      )
      response.raise_for_status()
      data = response.json()

      return PriceQuote(
        input_mint=data['inputMint'],
        output_mint=data['outputMint'],
        input_amount=int(data['inAmount']),
        output_amount=int(data['outAmount']),
        price_impact_pct=float(data.get('priceImpactPct', 0)),
        route_plan=data.get('routePlan', [])
      )
    except Exception as e:
      logger.error(f'Error getting price quote: {e}')
      return None

  @async_retry(max_retries=3, delay=1.0)
  async def get_swap_transaction(
    self,
    quote_response: Dict[str, Any],
    user_public_key: str,
    wrap_and_unwrap_sol: bool = True,
    prioritization_fee_lamports: int = 0
  ) -> Optional[SwapTransaction]:
    """
    Get swap transaction.

    Args:
        quote_response: Quote response from Jupiter API
        user_public_key: User's public key
        wrap_and_unwrap_sol: Whether to wrap/unwrap SOL
        prioritization_fee_lamports: Priority fee in lamports

    Returns:
        SwapTransaction or None
    """
    try:
      params = {
        'quoteResponse': quote_response,
        'userPublicKey': user_public_key,
        'wrapAndUnwrapSol': wrap_and_unwrap_sol,
        'prioritizationFeeLamports': prioritization_fee_lamports,
      }

      response = await self.client.post(
        f'{self.api_url}/swap',
        json=params
      )
      response.raise_for_status()
      data = response.json()

      return SwapTransaction(
        swap_transaction=data['swapTransaction'],
        last_valid_block_height=data['lastValidBlockHeight'],
        prioritization_fee_lamports=data.get('prioritizationFeeLamports', 0)
      )
    except Exception as e:
      logger.error(f'Error getting swap transaction: {e}')
      return None

  async def get_indexed_route_map(self) -> Dict[str, Any]:
    """
    Get indexed route map for better routing.

    Returns:
        Route map data
    """
    try:
      response = await self.client.get(
        'https://quote-api.jup.ag/v6/indexed-route-map'
      )
      response.raise_for_status()
      return response.json()
    except Exception as e:
      logger.error(f'Error getting route map: {e}')
      return {}

  async def get_tokens_by_mint(self, mint_addresses: List[str]) -> Dict[str, Any]:
    """
    Get token information by mint addresses.

    Args:
        mint_addresses: List of mint addresses

    Returns:
        Dictionary mapping mint addresses to token info
    """
    try:
      response = await self.client.get(
        'https://token.jup.ag/all'
      )
      response.raise_for_status()
      all_tokens = response.json()

      # Filter for requested mints
      mint_set = set(mint_addresses)
      token_map = {}
      for token in all_tokens:
        if token['address'] in mint_set:
          token_map[token['address']] = token

      return token_map
    except Exception as e:
      logger.error(f'Error getting tokens by mint: {e}')
      return {}

  def calculate_slippage_bps(self, percentage: float) -> int:
    """
    Convert percentage to basis points.

    Args:
        percentage: Slippage percentage (e.g., 0.5 for 0.5%)

    Returns:
        Basis points (50 for 0.5%)
    """
    return int(percentage * 100)

  def calculate_minimum_amount_out(self, output_amount: int, slippage_bps: int) -> int:
    """
    Calculate minimum output amount with slippage.

    Args:
        output_amount: Expected output amount
        slippage_bps: Slippage in basis points

    Returns:
        Minimum output amount
    """
    slippage_multiplier = 1 - (slippage_bps / 10000)
    return int(output_amount * slippage_multiplier)


# Common token addresses
SOL_MINT = 'So11111111111111111111111111111111111111112'  # Wrapped SOL
USDC_MINT = 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'
USDT_MINT = 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB'


# Global client instance
_jupiter_client: Optional[JupiterClient] = None


def get_jupiter_client() -> JupiterClient:
  """Get global Jupiter client instance."""
  global _jupiter_client
  if _jupiter_client is None:
    _jupiter_client = JupiterClient()
  return _jupiter_client
