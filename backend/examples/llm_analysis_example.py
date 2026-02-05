"""
Example usage of LLM analysis engine.

This script demonstrates how to:
1. Calculate technical indicators
2. Generate trading signals using LLM
3. Evaluate signal quality
4. Execute trades based on signals
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services import get_market_data_client
from src.services.signal_service import get_signal_service
from src.services.trading_manager import get_trading_manager
from src.services.technical_indicators import TechnicalIndicators
from src.utils import logger, format_usd


async def example_technical_indicators():
  """Example: Calculate technical indicators."""
  logger.info('=== Calculating Technical Indicators ===')

  # Generate sample price data
  # In production, you'd fetch this from an API
  base_price = 100.0
  price_history = []

  for i in range(100):
    # Simulate price movement with trend and noise
    trend = i * 0.1
    noise = (i % 10 - 5) * 0.5
    price = base_price + trend + noise

    price_history.append({
      'price': price,
      'high': price + 0.5,
      'low': price - 0.5,
      'timestamp': datetime.utcnow() - timedelta(hours=100 - i)
    })

  # Extract prices
  prices = [p['price'] for p in price_history]

  # Calculate indicators
  sma_20 = TechnicalIndicators.sma(prices, 20)
  ema_12 = TechnicalIndicators.ema(prices, 12)
  rsi = TechnicalIndicators.rsi(prices, 14)
  macd = TechnicalIndicators.macd(prices)
  bb = TechnicalIndicators.bollinger_bands(prices)
  trend = TechnicalIndicators.analyze_trend(prices)
  sr = TechnicalIndicators.get_support_resistance(prices)

  logger.info(f'SMA(20): {format_usd(sma_20) if sma_20 else "N/A"}')
  logger.info(f'EMA(12): {format_usd(ema_12) if ema_12 else "N/A"}')
  logger.info(f'RSI(14): {rsi:.2f}' if rsi else 'RSI: N/A')

  if rsi:
    if rsi > 70:
      logger.info(f'RSI Signal: Overbought (sell signal)')
    elif rsi < 30:
      logger.info(f'RSI Signal: Oversold (buy signal)')
    else:
      logger.info(f'RSI Signal: Neutral')

  if macd:
    logger.info(f'MACD: {macd["macd"]:.4f}')

  if bb:
    logger.info(f'Bollinger Bands: Upper={bb["upper"]:.2f}, Middle={bb["middle"]:.2f}, Lower={bb["lower"]:.2f}')

  logger.info(f'Trend: {trend["trend"]} ({trend["strength"]})')
  logger.info(f'Support Levels: {[f"${s:.2f}" for s in sr["support"]]}')
  logger.info(f'Resistance Levels: {[f"${r:.2f}" for r in sr["resistance"]]}')


async def example_generate_signal():
  """Example: Generate trading signal using LLM."""
  logger.info('=== Generating Trading Signal ===')

  signal_service = get_signal_service()

  # Get SOL market data
  market_client = get_market_data_client()
  sol_price = await market_client.get_sol_price()

  logger.info(f'Current SOL Price: {format_usd(sol_price)}')

  # Generate sample price history for technical analysis
  # In production, you'd fetch this from a price API
  price_history = []
  for i in range(100):
    price = sol_price * (1 + (i % 20 - 10) * 0.01)  # +/- 10% variation
    price_history.append({
      'price': price,
      'high': price * 1.005,
      'low': price * 0.995,
      'timestamp': datetime.utcnow() - timedelta(hours=100 - i)
    })

  # Generate signal
  signal = await signal_service.generate_signal(
    token_address='So11111111111111111111111111111111111111112',  # Wrapped SOL
    token_symbol='SOL',
    price_history=price_history,
    context={
      'market_sentiment': 'neutral',
      'major_news': ['Solana network activity increasing']
    }
  )

  if signal:
    logger.info(f'\n=== Signal Generated ===')
    logger.info(f'Action: {signal.action.upper()}')
    logger.info(f'Strength: {signal.strength}')
    logger.info(f'Confidence: {signal.confidence:.2f}')
    logger.info(f'Risk Level: {signal.risk_level}')
    logger.info(f'\nReasoning:\n{signal.reasoning}')

    if signal.entry_price:
      logger.info(f'\nEntry Price: {format_usd(signal.entry_price)}')
    if signal.stop_loss:
      logger.info(f'Stop Loss: {format_usd(signal.stop_loss)}')
    if signal.take_profit:
      logger.info(f'Take Profit: {format_usd(signal.take_profit)}')
    if signal.position_size_percent:
      logger.info(f'Suggested Position Size: {signal.position_size_percent:.1f}%')

    # Evaluate if signal should be executed
    should_execute, reason = signal_service.should_execute_signal(signal)
    logger.info(f'\nExecute Signal: {"YES" if should_execute else "NO"}')
    logger.info(f'Reason: {reason}')
  else:
    logger.warning('Failed to generate signal')


async def example_signal_history():
  """Example: Get signal history."""
  logger.info('=== Signal History ===')

  signal_service = get_signal_service()

  signals = signal_service.get_recent_signals(limit=10)
  logger.info(f'Recent Signals: {len(signals)}')

  for signal in signals:
    logger.info(f'\n{signal["timestamp"]} | '
               f'{signal["token_symbol"]} | '
               f'{signal["action"].upper()} | '
               f'Confidence: {signal["confidence"]:.2f} | '
               f'Risk: {signal["risk_level"]}')


async def example_trade_on_signal():
  """Example: Execute trade based on signal."""
  logger.info('=== Trading on Signal ===')

  signal_service = get_signal_service()
  trading_manager = get_trading_manager()

  # Generate signal
  signal = await signal_service.generate_signal(
    token_address='EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',  # USDC
    token_symbol='USDC',
    price_history=[],  # Would fetch real history
    context={}
  )

  if not signal:
    logger.error('Failed to generate signal')
    return

  # Check if should execute
  should_execute, reason = signal_service.should_execute_signal(signal)

  if should_execute and signal.action == 'buy':
    logger.info(f'Signal indicates BUY, executing trade...')

    # Calculate position size
    portfolio = await trading_manager.get_portfolio_value()
    if portfolio:
      available_sol = portfolio.available_balance_sol

      # Use suggested position size or default to 5%
      position_percent = signal.position_size_percent or 5.0
      amount_sol = (available_sol * position_percent / 100)

      logger.info(f'Position Size: {position_percent:.1f}% ({amount_sol:.4f} SOL)')

      # Execute trade (commented out - requires wallet configuration)
      # from src.models import TradeType
      # trade = await trading_manager.execute_trade_with_validation(
      #   token_mint=signal.token_address,
      #   token_symbol=signal.token_symbol,
      #   amount_sol=amount_sol,
      #   trade_type=TradeType.BUY
      # )

      # if trade:
      #   logger.info(f'Trade executed successfully!')
      # else:
      #   logger.error('Trade execution failed')

  else:
    logger.info(f'Not executing trade: {reason}')


async def main():
  """Run all examples."""
  logger.info('LLM Analysis Engine Examples')
  logger.info('=' * 50)

  try:
    await example_technical_indicators()
    print()

    await example_generate_signal()
    print()

    await example_signal_history()
    print()

    await example_trade_on_signal()
    print()

  except Exception as e:
    logger.error(f'Error running examples: {e}')
    import traceback
    traceback.print_exc()


if __name__ == '__main__':
  asyncio.run(main())
