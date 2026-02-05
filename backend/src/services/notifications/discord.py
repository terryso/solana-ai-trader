import httpx
from typing import Optional
from datetime import datetime

from src.config import settings
from src.utils import logger, format_usd, async_retry


class DiscordNotifier:
  """Discord webhook notification service."""

  def __init__(
    self,
    webhook_url: Optional[str] = None
  ):
    """
    Initialize Discord notifier.

    Args:
        webhook_url: Discord webhook URL (defaults to settings)
    """
    self.webhook_url = webhook_url or settings.discord_webhook_url
    self.client = httpx.AsyncClient(timeout=30.0)

  async def close(self):
    """Close HTTP client."""
    await self.client.aclose()

  def is_configured(self) -> bool:
    """
    Check if Discord is properly configured.

    Returns:
        True if webhook URL is set
    """
    return bool(self.webhook_url)

  @async_retry(max_retries=3, delay=1.0)
  async def send_message(
    self,
    content: Optional[str] = None,
    embeds: Optional[list] = None,
    username: Optional[str] = None
  ) -> bool:
    """
    Send a message via Discord webhook.

    Args:
        content: Message content
        embeds: List of embed objects
        username: Override username

    Returns:
        True if successful
    """
    if not self.is_configured():
      logger.warning('Discord not configured, skipping notification')
      return False

    try:
      payload = {}

      if content:
        payload['content'] = content

      if embeds:
        payload['embeds'] = embeds

      if username:
        payload['username'] = username

      response = await self.client.post(self.webhook_url, json=payload)
      response.raise_for_status()
      return True

    except Exception as e:
      logger.error(f'Error sending Discord message: {e}')
      return False

  async def send_trade_notification(
    self,
    trade_type: str,
    token_symbol: str,
    amount: float,
    price: float,
    value_usd: float,
    status: str = 'executed',
    signature: Optional[str] = None
  ) -> bool:
    """
    Send trade execution notification.

    Args:
        trade_type: Type of trade (buy/sell)
        token_symbol: Token symbol
        amount: Amount traded
        price: Price per token
        value_usd: Value in USD
        status: Trade status
        signature: Transaction signature

    Returns:
        True if successful
    """
    emoji = '🟢' if trade_type == 'buy' else '🔴'
    color = 0x00ff00 if trade_type == 'buy' else 0xff0000

    embed = {
      'title': f'{emoji} Trade {status.upper()}',
      'color': color,
      'fields': [
        {'name': 'Type', 'value': trade_type.upper(), 'inline': True},
        {'name': 'Token', 'value': token_symbol, 'inline': True},
        {'name': 'Amount', 'value': f'{amount:.6f}', 'inline': True},
        {'name': 'Price', 'value': format_usd(price), 'inline': True},
        {'name': 'Value', 'value': format_usd(value_usd), 'inline': True},
        {'name': 'Status', 'value': status.upper(), 'inline': True},
      ],
      'timestamp': datetime.utcnow().isoformat()
    }

    if signature:
      embed['fields'].append({
        'name': 'Transaction',
        'value': f'`{signature[:8]}...{signature[-8:]}`',
        'inline': False
      })

    return await self.send_message(
        username='Solana AI Trader',
        embeds=[embed]
    )

  async def send_signal_notification(
    self,
    action: str,
    token_symbol: str,
    strength: str,
    confidence: float,
    risk_level: str,
    reasoning: str,
    entry_price: Optional[float] = None
  ) -> bool:
    """
    Send trading signal notification.

    Args:
        action: Signal action (buy/sell/hold)
        token_symbol: Token symbol
        strength: Signal strength
        confidence: Confidence level
        risk_level: Risk level
        reasoning: Analysis reasoning
        entry_price: Suggested entry price

    Returns:
        True if successful
    """
    emoji_map = {
      'buy': '🟢',
      'sell': '🔴',
      'hold': '⏸️'
    }

    emoji = emoji_map.get(action, '📊')
    color = 0x00ff00 if action == 'buy' else 0xff0000 if action == 'sell' else 0xffff00

    embed = {
      'title': f'{emoji} New Trading Signal',
      'color': color,
      'fields': [
        {'name': 'Action', 'value': action.upper(), 'inline': True},
        {'name': 'Token', 'value': token_symbol, 'inline': True},
        {'name': 'Strength', 'value': strength, 'inline': True},
        {'name': 'Confidence', 'value': f'{confidence:.0%}', 'inline': True},
        {'name': 'Risk Level', 'value': risk_level, 'inline': True},
      ],
      'description': f'*{reasoning}*' if reasoning else None,
      'timestamp': datetime.utcnow().isoformat()
    }

    if entry_price:
      embed['fields'].append({
        'name': 'Entry Price',
        'value': format_usd(entry_price),
        'inline': True
      })

    return await self.send_message(
      username='Solana AI Trader',
      embeds=[embed]
    )

  async def test_connection(self) -> bool:
    """
    Test Discord connection.

    Returns:
        True if connection successful
    """
    if not self.is_configured():
      logger.warning('Discord not configured')
      return False

    embed = {
      'title': '✅ Discord Notification Test',
      'description': 'Solana AI Trader is connected successfully!',
      'color': 0x00ff00,
      'fields': [
        {'name': 'System', 'value': 'Solana AI Trader', 'inline': True},
        {'name': 'Status', 'value': 'Connected', 'inline': True}
      ]
    }

    return await self.send_message(
      username='Solana AI Trader',
      embeds=[embed]
    )


# Global notifier instance
_discord_notifier: Optional[DiscordNotifier] = None


def get_discord_notifier() -> DiscordNotifier:
  """Get global Discord notifier instance."""
  global _discord_notifier
  if _discord_notifier is None:
    _discord_notifier = DiscordNotifier()
  return _discord_notifier
