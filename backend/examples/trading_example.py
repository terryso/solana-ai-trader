"""
Example usage of Jupiter trading integration.

This script demonstrates how to:
1. Get token prices
2. Simulate swaps
3. Execute trades
4. Get portfolio information
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.jupiter_client import get_jupiter_client, SOL_MINT
from src.services.market_data import get_market_data_client
from src.services.trading_executor import get_trading_executor
from src.services.trading_manager import get_trading_manager
from src.utils import logger, format_sol, format_usd


async def example_get_prices():
  """Example: Get token prices."""
  logger.info('=== Getting Token Prices ===')

  client = get_market_data_client()

  # Get SOL price
  sol_price = await client.get_sol_price()
  logger.info(f'SOL Price: {format_usd(sol_price)}')

  # Get price for a specific token (e.g., USDC)
  usdc_price = await client.get_token_price(
    'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'
  )
  logger.info(f'USDC Price: {format_usd(usdc_price)}')


async def example_simulate_swap():
  """Example: Simulate a swap."""
  logger.info('=== Simulating Swap ===')

  executor = get_trading_executor()

  # Simulate swapping 1 SOL to USDC
  result = await executor.simulate_swap(
    input_mint=SOL_MINT,
    output_mint='EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
    amount=1.0
  )

  if result:
    logger.info(f'Input: {format_sol(result["input_amount"])}')
    logger.info(f'Output: ${result["output_amount"]:.2f} USDC')
    logger.info(f'Price Impact: {result["price_impact_pct"]:.2f}%')
    logger.info(f'Hops: {result["route_count"]}')


async def example_get_wallet_info():
  """Example: Get wallet information."""
  logger.info('=== Getting Wallet Info ===')

  executor = get_trading_executor()

  # Get wallet address (if configured)
  address = await executor.get_wallet_address()
  if address:
    logger.info(f'Wallet Address: {address}')
  else:
    logger.info('No wallet configured')

  # Get SOL balance
  balance = await executor.get_wallet_balance()
  logger.info(f'SOL Balance: {format_sol(balance)}')


async def example_get_portfolio():
  """Example: Get portfolio information."""
  logger.info('=== Getting Portfolio Info ===')

  manager = get_trading_manager()

  portfolio = await manager.get_portfolio_value()
  if portfolio:
    logger.info(f'Total Portfolio Value: {format_usd(portfolio.total_value_usd)}')
    logger.info(f'Available SOL: {format_sol(portfolio.available_balance_sol)}')
    logger.info(f'Open Positions: {len(portfolio.positions)}')
    logger.info(f'Unrealized PnL: {format_usd(portfolio.unrealized_pnl_usd)} '
               f'({portfolio.unrealized_pnl_percentage:.2f}%)')

    for position in portfolio.positions:
      logger.info(f'  - {position.token_symbol}: '
                 f'{position.amount:.4f} @ ${position.current_price:.4f} | '
                 f'PnL: {format_usd(position.pnl_usd)} ({position.pnl_percentage:.2f}%)')


async def example_trade_validation():
  """Example: Validate a trade."""
  logger.info('=== Validating Trade ===')

  executor = get_trading_executor()

  # Check if a 0.5 SOL trade would be valid
  is_valid, error_msg = await executor.validate_trade(
    amount=0.5,
    token_mint='EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'
  )

  if is_valid:
    logger.info('Trade validation: PASSED')
  else:
    logger.warning(f'Trade validation: FAILED - {error_msg}')


async def example_get_trade_history():
  """Example: Get trade history."""
  logger.info('=== Getting Trade History ===')

  manager = get_trading_manager()

  trades = manager.get_trade_history(limit=10)
  logger.info(f'Recent Trades: {len(trades)}')

  for trade in trades:
    logger.info(f'  {trade["timestamp"]} | '
               f'{trade["type"].upper()} {trade["token_symbol"]} | '
               f'{format_sol(trade["amount"])} @ ${trade["price"]:.4f} | '
               f'Status: {trade["status"]}')


async def example_daily_pnl():
  """Example: Get daily PnL."""
  logger.info('=== Getting Daily PnL ===')

  manager = get_trading_manager()

  pnl = manager.get_daily_pnl()
  logger.info(f'Total Bought: {format_usd(pnl["total_bought_usd"])}')
  logger.info(f'Total Sold: {format_usd(pnl["total_sold_usd"])}')
  logger.info(f'Net PnL: {format_usd(pnl["pnl_usd"])}')
  logger.info(f'Trade Count: {pnl["trade_count"]}')


async def main():
  """Run all examples."""
  logger.info('Jupiter Trading Integration Examples')
  logger.info('=' * 50)

  try:
    await example_get_prices()
    print()

    await example_simulate_swap()
    print()

    await example_get_wallet_info()
    print()

    await example_get_portfolio()
    print()

    await example_trade_validation()
    print()

    await example_get_trade_history()
    print()

    await example_daily_pnl()
    print()

  except Exception as e:
    logger.error(f'Error running examples: {e}')
  finally:
    # Close clients
    jupiter_client = get_jupiter_client()
    await jupiter_client.close()

    market_client = get_market_data_client()
    await market_client.close()

    solana_client = executor.solana if (executor := get_trading_executor()) else None
    if solana_client:
      await solana_client.close()


if __name__ == '__main__':
  asyncio.run(main())
