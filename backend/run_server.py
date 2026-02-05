"""
Development server for Solana AI Trader web dashboard.

Run this script to start the web interface:
  python run_server.py

Then open: http://localhost:8000
"""

import uvicorn
from src.config import settings
from src.api import app
from src.database import init_db
from src.utils import logger


def main():
  """Start the development server."""
  # Initialize database
  init_db()
  logger.info('Database initialized')

  # Start server
  logger.info(f'Starting server on http://localhost:8000')
  logger.info(f'Environment: {settings.environment}')

  uvicorn.run(
    app,
    host='0.0.0.0',
    port=8000,
    reload=True,  # Auto-reload on code changes
    log_level='info'
  )


if __name__ == '__main__':
  main()
