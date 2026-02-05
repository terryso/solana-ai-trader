"""
Example usage of Telegram and Discord notifications.

This script demonstrates how to:
1. Test notification connection
2. Send trade notifications
3. Send signal notifications
4. Send portfolio updates
5. Send daily summaries
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.notifications import get_telegram_notifier, get_discord_notifier
from src.utils import logger


async def example_telegram_test():
  """Example: Test Telegram connection."""
  logger.info('=== Testing Telegram Connection ===')

  telegram = get_telegram_notifier()

  if not telegram.is_configured():
    logger.warning('Telegram not configured. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env')
    return

  success = await telegram.test_connection()

  if success:
    logger.info('✅ Telegram connection successful!')
  else:
    logger.error('❌ Telegram connection failed')


async def example_discord_test():
  """Example: Test Discord connection."""
  logger.info('=== Testing Discord Connection ===')

  discord = get_discord_notifier()

  if not discord.is_configured():
    logger.warning('Discord not configured. Set DISCORD_WEBHOOK_URL in .env')
    return

  success = await discord.test_connection()

  if success:
    logger.info('✅ Discord connection successful!')
  else:
    logger.error('❌ Discord connection failed')


async def example_trade_notifications():
  """Example: Send trade notifications."""
  logger.info('=== Sending Trade Notifications ===')

  telegram = get_telegram_notifier()
  discord = get_discord_notifier()

  # Simulate a buy trade
  if telegram.is_configured():
    await telegram.send_trade_notification(
      trade_type='buy',
      token_symbol='SOL',
      amount=10.5,
      price=145.50,
      value_usd=1527.75,
      status='executed',
      signature='abc123xyz789'
    )
    logger.info('Sent Telegram buy notification')

  if discord.is_configured():
    await discord.send_trade_notification(
      trade_type='buy',
      token_symbol='SOL',
      amount=10.5,
      price=145.50,
      value_usd=1527.75,
      status='executed',
      signature='abc123xyz789'
    )
    logger.info('Sent Discord buy notification')

  # Simulate a sell trade
  if telegram.is_configured():
    await telegram.send_trade_notification(
      trade_type='sell',
      token_symbol='USDC',
      amount=1000.0,
      price=1.00,
      value_usd=1000.00,
      status='executed',
      signature='def456uvw012'
    )
    logger.info('Sent Telegram sell notification')


async def example_signal_notifications():
  """Example: Send signal notifications."""
  logger.info('=== Sending Signal Notifications ===')

  telegram = get_telegram_notifier()
  discord = get_discord_notifier()

  # Simulate a buy signal
  if telegram.is_configured():
    await telegram.send_signal_notification(
      action='buy',
      token_symbol='BONK',
      strength='strong',
      confidence=0.85,
      risk_level='medium',
      reasoning='RSI indicates oversold conditions, MACD crossover detected, increasing volume on Solana DEXs.',
      entry_price=0.000025
    )
    logger.info('Sent Telegram signal notification')

  if discord.is_configured():
    await discord.send_signal_notification(
      action='buy',
      token_symbol='BONK',
      strength='strong',
      confidence=0.85,
      risk_level='medium',
      reasoning='RSI indicates oversold conditions, MACD crossover detected, increasing volume on Solana DEXs.',
      entry_price=0.000025
    )
    logger.info('Sent Discord signal notification')


async def example_portfolio_update():
  """Example: Send portfolio update."""
  logger.info('=== Sending Portfolio Update ===')

  telegram = get_telegram_notifier()

  if telegram.is_configured():
    await telegram.send_portfolio_update(
      total_value_usd=5432.10,
      unrealized_pnl_usd=234.50,
      unrealized_pnl_percentage=4.51,
      position_count=3
    )
    logger.info('Sent portfolio update notification')


async def example_daily_summary():
  """Example: Send daily trading summary."""
  logger.info('=== Sending Daily Summary ===')

  telegram = get_telegram_notifier()

  if telegram.is_configured():
    await telegram.send_daily_summary(
      total_trades=15,
      total_bought_usd=3200.00,
      total_sold_usd=3434.50,
      pnl_usd=234.50,
      best_trade={'token_symbol': 'SOL', 'pnl': 150.00},
      worst_trade={'token_symbol': 'WIF', 'pnl': -25.00}
    )
    logger.info('Sent daily summary notification')


async def example_error_alert():
  """Example: Send error alert."""
  logger.info('=== Sending Error Alert ===')

  telegram = get_telegram_notifier()

  if telegram.is_configured():
    await telegram.send_error_alert(
      error_type='Trade Execution Failed',
      error_message='Insufficient liquidity for trade',
      context='Attempting to buy 1000 XYZ tokens'
    )
    logger.info('Sent error alert notification')


async def main():
  """Run all examples."""
  logger.info('Notification System Examples')
  logger.info('=' * 50)

  try:
    # Test connections
    await example_telegram_test()
    print()

    await example_discord_test()
    print()

    # Only send other notifications if at least one service is configured
    telegram = get_telegram_notifier()
    discord = get_discord_notifier()

    if not (telegram.is_configured() or discord.is_configured()):
      logger.warning('No notification services configured. Please set up Telegram or Discord.')
      logger.info('')
      logger.info('How to set up:')
      logger.info('')
      logger.info('Telegram:')
      logger.info('1. Create a bot via @BotFather on Telegram')
      logger.info('2. Get your bot token')
      logger.info('3. Get your chat ID (message @userinfobot)')
      logger.info('4. Add to .env:')
      logger.info('   TELEGRAM_BOT_TOKEN=your_bot_token')
      logger.info('   TELEGRAM_CHAT_ID=your_chat_id')
      logger.info('')
      logger.info('Discord:')
      logger.info('1. Server Settings → Integrations → Webhooks')
      logger.info('2. Create webhook and copy URL')
      logger.info('3. Add to .env:')
      logger.info('   DISCORD_WEBHOOK_URL=your_webhook_url')
      return

    # Send example notifications
    await example_trade_notifications()
    print()

    await example_signal_notifications()
    print()

    await example_portfolio_update()
    print()

    await example_daily_summary()
    print()

    await example_error_alert()
    print()

  except Exception as e:
    logger.error(f'Error running examples: {e}')
    import traceback
    traceback.print_exc()
  finally:
    # Close clients
    telegram = get_telegram_notifier()
    await telegram.close()

    discord = get_discord_notifier()
    await discord.close()


if __name__ == '__main__':
  asyncio.run(main())
