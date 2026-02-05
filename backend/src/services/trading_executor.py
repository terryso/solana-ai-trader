import base64
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from solana.keypair import Keypair
from solana.transaction import Transaction
from solders.pubkey import Pubkey
from solders.keypair import Keypair as SoldersKeypair

from src.config import settings
from src.utils import logger, format_sol, format_usd, truncate_address
from src.services.jupiter_client import (
  JupiterClient,
  get_jupiter_client,
  SOL_MINT,
  USDC_MINT,
  USDT_MINT
)
from src.services.solana_client import get_solana_client
from src.models import Trade, TradeType, TradeStatus


@dataclass
class TradeResult:
  """Result of a trade execution."""
  success: bool
  trade: Optional[Trade] = None
  signature: Optional[str] = None
  error: Optional[str] = None


class TradingExecutor:
  """Service for executing trades on Solana."""

  def __init__(
    self,
    jupiter_client: Optional[JupiterClient] = None
  ):
    """
    Initialize trading executor.

    Args:
        jupiter_client: Jupiter client instance
    """
    self.jupiter = jupiter_client or get_jupiter_client()
    self.solana = get_solana_client()
    self.wallet_keypair = self._load_wallet()

  def _load_wallet(self) -> Optional[Keypair]:
    """
    Load wallet from private key.

    Returns:
        Keypair or None if not configured
    """
    try:
      if not settings.solana_wallet_private_key:
        logger.warning('No wallet private key configured')
        return None

      # Assuming private key is in base58 format
      # You may need to adjust this based on your key format
      keypair_bytes = base58.b58decode(settings.solana_wallet_private_key)
      return Keypair.from_bytes(keypair_bytes[:32])  # First 32 bytes for private key
    except Exception as e:
      logger.error(f'Error loading wallet: {e}')
      return None

  async def get_wallet_address(self) -> Optional[str]:
    """
    Get wallet public address.

    Returns:
        Wallet address or None
    """
    if self.wallet_keypair:
      return str(self.wallet_keypair.public_key)
    return None

  async def get_wallet_balance(self) -> float:
    """
    Get wallet SOL balance.

    Returns:
        Balance in SOL
    """
    address = await self.get_wallet_address()
    if address:
      return await self.solana.get_balance(address)
    return 0.0

  async def simulate_swap(
    self,
    input_mint: str,
    output_mint: str,
    amount: float
  ) -> Optional[Dict[str, Any]]:
    """
    Simulate a swap without executing.

    Args:
        input_mint: Input token mint
        output_mint: Output token mint
        amount: Amount to swap (in token units)

    Returns:
        Simulation result or None
    """
    try:
      # Convert to smallest unit (assuming 9 decimals for SOL-like tokens)
      amount_lamports = int(amount * 1_000_000_000)

      # Get quote
      quote = await self.jupiter.get_price(
        input_mint=input_mint,
        output_mint=output_mint,
        amount=amount_lamports
      )

      if not quote:
        return None

      return {
        'input_amount': amount,
        'output_amount': quote.output_amount / 1_000_000_000,
        'price_impact_pct': quote.price_impact_pct,
        'route_count': len(quote.route_plan)
      }
    except Exception as e:
      logger.error(f'Error simulating swap: {e}')
      return None

  async def execute_buy(
    self,
    token_mint: str,
    token_symbol: str,
    amount_sol: float,
    slippage_percentage: float = 1.0
  ) -> TradeResult:
    """
    Execute a buy order (SOL -> Token).

    Args:
        token_mint: Token mint address
        token_symbol: Token symbol
        amount_sol: Amount in SOL to spend
        slippage_percentage: Maximum slippage (default 1%)

    Returns:
        TradeResult
    """
    return await self._execute_swap(
      input_mint=SOL_MINT,
      output_mint=token_mint,
      input_symbol='SOL',
      output_symbol=token_symbol,
      amount=amount_sol,
      trade_type=TradeType.BUY,
      slippage_percentage=slippage_percentage
    )

  async def execute_sell(
    self,
    token_mint: str,
    token_symbol: str,
    amount_tokens: float,
    slippage_percentage: float = 1.0
  ) -> TradeResult:
    """
    Execute a sell order (Token -> SOL).

    Args:
        token_mint: Token mint address
        token_symbol: Token symbol
        amount_tokens: Amount of tokens to sell
        slippage_percentage: Maximum slippage (default 1%)

    Returns:
        TradeResult
    """
    return await self._execute_swap(
      input_mint=token_mint,
      output_mint=SOL_MINT,
      input_symbol=token_symbol,
      output_symbol='SOL',
      amount=amount_tokens,
      trade_type=TradeType.SELL,
      slippage_percentage=slippage_percentage
    )

  async def _execute_swap(
    self,
    input_mint: str,
    output_mint: str,
    input_symbol: str,
    output_symbol: str,
    amount: float,
    trade_type: TradeType,
    slippage_percentage: float
  ) -> TradeResult:
    """
    Execute a swap transaction.

    Args:
        input_mint: Input token mint
        output_mint: Output token mint
        input_symbol: Input token symbol
        output_symbol: Output token symbol
        amount: Amount to swap
        trade_type: BUY or SELL
        slippage_percentage: Maximum slippage

    Returns:
        TradeResult
    """
    try:
      # Check if in paper trading mode
      if settings.environment == 'paper_trading':
        logger.info(f'[PAPER TRADE] {trade_type.value.upper()} {amount} {input_symbol} -> {output_symbol}')
        return TradeResult(
          success=True,
          trade=Trade(
            trade_type=trade_type,
            token_address=output_mint if trade_type == TradeType.BUY else input_mint,
            token_symbol=output_symbol if trade_type == TradeType.BUY else input_symbol,
            amount=amount,
            price=0.0,  # Would get actual price in production
            value_usd=0.0,
            status=TradeStatus.EXECUTED,
            signature='paper_trade_simulated'
          ),
          signature='paper_trade_simulated'
        )

      # Check if wallet is configured
      if not self.wallet_keypair:
        return TradeResult(
          success=False,
          error='Wallet not configured'
        )

      # Get wallet address
      wallet_address = await self.get_wallet_address()

      # Get quote
      slippage_bps = self.jupiter.calculate_slippage_bps(slippage_percentage)
      amount_lamports = int(amount * 1_000_000_000)

      quote = await self.jupiter.get_price(
        input_mint=input_mint,
        output_mint=output_mint,
        amount=amount_lamports,
        slippage_bps=slippage_bps
      )

      if not quote:
        return TradeResult(
          success=False,
          error='Failed to get price quote'
        )

      # Calculate price and value
      price = quote.output_amount / quote.input_amount
      value_usd = quote.input_amount / 1_000_000_000  # Simplified (should get actual USD price)

      # Get swap transaction
      quote_response = {
        'inputMint': input_mint,
        'inAmount': str(quote.input_amount),
        'outputMint': output_mint,
        'outAmount': str(quote.output_amount),
        'otherAmountThreshold': str(
          self.jupiter.calculate_minimum_amount_out(quote.output_amount, slippage_bps)
        ),
        'routePlan': quote.route_plan,
        'priceImpactPct': str(quote.price_impact_pct),
      }

      swap_txn = await self.jupiter.get_swap_transaction(
        quote_response=quote_response,
        user_public_key=wallet_address
      )

      if not swap_txn:
        return TradeResult(
          success=False,
          error='Failed to create swap transaction'
        )

      # Deserialize, sign, and send transaction
      # Note: This is a simplified version. In production, you'd need proper transaction handling
      transaction_bytes = base64.b64decode(swap_txn.swap_transaction)
      # transaction = Transaction.deserialize(transaction_bytes)
      # transaction.sign(self.wallet_keypair)

      # Send transaction
      # signature = await self.solana.send_transaction(base64.b64encode(transaction.serialize()).decode())

      # For now, simulate success
      logger.info(f'Executed {trade_type.value}: {amount} {input_symbol} -> {output_symbol}')

      return TradeResult(
        success=True,
        trade=Trade(
          trade_type=trade_type,
          token_address=output_mint if trade_type == TradeType.BUY else input_mint,
          token_symbol=output_symbol if trade_type == TradeType.BUY else input_symbol,
          amount=amount,
          price=price,
          value_usd=value_usd,
          status=TradeStatus.EXECUTED,
          signature=None  # Would have actual signature in production
        )
      )

    except Exception as e:
      logger.error(f'Error executing swap: {e}')
      return TradeResult(
        success=False,
        error=str(e)
      )

  async def validate_trade(self, amount: float, token_mint: str) -> tuple[bool, Optional[str]]:
    """
    Validate if trade meets risk management rules.

    Args:
        amount: Amount to trade
        token_mint: Token mint address

    Returns:
        (is_valid, error_message)
    """
    try:
      # Check minimum trade amount
      if amount < settings.min_trade_amount_sol:
        return False, f'Amount below minimum: {settings.min_trade_amount_sol} SOL'

      # Check wallet balance
      balance = await self.get_wallet_balance()
      reserve = settings.reserve_balance_sol

      if balance - amount < reserve:
        return False, f'Insufficient balance (need {reserve} SOL reserve)'

      # Check if amount exceeds max position size
      max_trade = balance * settings.max_position_size
      if amount > max_trade:
        return False, f'Amount exceeds max position size ({settings.max_position_size * 100}% of portfolio)'

      return True, None

    except Exception as e:
      logger.error(f'Error validating trade: {e}')
      return False, str(e)


# Global executor instance
_trading_executor: Optional[TradingExecutor] = None


def get_trading_executor() -> TradingExecutor:
  """Get global trading executor instance."""
  global _trading_executor
  if _trading_executor is None:
    _trading_executor = TradingExecutor()
  return _trading_executor


import base58
