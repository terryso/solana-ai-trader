import logging
import sys
from pathlib import Path
from pythonjsonlogger import jsonlogger

from src.config import settings


def setup_logger(name: str = 'solana_ai_trader') -> logging.Logger:
  """
  Setup logger with JSON formatting.

  Args:
      name: Logger name

  Returns:
      Configured logger
  """
  logger = logging.getLogger(name)

  # Set log level
  log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
  logger.setLevel(log_level)

  # Remove existing handlers
  logger.handlers.clear()

  # Console handler
  console_handler = logging.StreamHandler(sys.stdout)
  console_handler.setLevel(log_level)

  # File handler
  log_dir = Path(settings.log_file).parent
  log_dir.mkdir(parents=True, exist_ok=True)

  file_handler = logging.FileHandler(settings.log_file, encoding='utf-8')
  file_handler.setLevel(log_level)

  # JSON formatter
  formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(name)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
  )

  console_handler.setFormatter(formatter)
  file_handler.setFormatter(formatter)

  logger.addHandler(console_handler)
  logger.addHandler(file_handler)

  return logger


# Global logger instance
logger = setup_logger()
