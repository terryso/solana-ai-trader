"""
Main entry point for Solana AI Trader.
"""

import asyncio
from pathlib import Path

from src.config import settings
from src.database import init_db
from src.utils import logger


async def main():
  """Main function."""
  logger.info('Starting Solana AI Trader...')
  logger.info(f'Environment: {settings.environment}')
  logger.info(f'Network: {settings.solana_network}')

  # Initialize database
  init_db()
  logger.info('Database initialized')

  # TODO: Implement main trading logic
  if settings.environment == 'production':
    logger.warning('PRODUCTION MODE - Real trades will be executed!')
  elif settings.environment == 'paper_trading':
    logger.info('PAPER TRADING MODE - No real trades')
  else:
    logger.info('DEVELOPMENT MODE - Testing only')

  logger.info('Solana AI Trader started')


if __name__ == '__main__':
  asyncio.run(main())
