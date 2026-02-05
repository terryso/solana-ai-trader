import httpx
from typing import Optional, List
from datetime import datetime

from src.config import settings
from src.utils import logger, format_usd, format_sol, async_retry


class TelegramNotifier:
  """Telegram notification service."""

  def __init__(
    self,
    bot_token: Optional[str] = None,
    chat_id: Optional[str] = None
  ):
    """
    Initialize Telegram notifier.

    Args:
        bot_token: Telegram bot token (defaults to settings)
        chat_id: Telegram chat ID (defaults to settings)
    """
    self.bot_token = bot_token or settings.telegram_bot_token
    self.chat_id = chat_id or settings.telegram_chat_id
    self.base_url = f'https://api.telegram.org/bot{self.bot_token}'
    self.client = httpx.AsyncClient(timeout=30.0)

  async def close(self):
    """Close HTTP client."""
    await self.client.aclose()

  def is_configured(self) -> bool:
    """
    Check if Telegram is properly configured.

    Returns:
        True if bot token and chat ID are set
    """
    return bool(self.bot_token and self.chat_id)

  @async_retry(max_retries=3, delay=1.0)
  async def send_message(
    self,
    text: str,
    parse_mode: str = 'HTML',
    disable_notification: bool = False
  ) -> bool:
    """
    Send a text message via Telegram.

    Args:
        text: Message text
        parse_mode: Parse mode (HTML, Markdown, or None)
        disable_notification: Send silently without notification

    Returns:
        True if successful
    """
    if not self.is_configured():
      logger.warning('Telegram not configured, skipping notification')
      return False

    try:
      response = await self.client.post(
        f'{self.base_url}/sendMessage',
        json={
          'chat_id': self.chat_id,
          'text': text,
          'parse_mode': parse_mode,
          'disable_notification': disable_notification
        }
      )
      response.raise_for_status()
      return True

    except Exception as e:
      logger.error(f'Error sending Telegram message: {e}')
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
    status_emoji = '✅' if status == 'executed' else '⏳' if status == 'pending' else '❌'

    message = f'''<b>{emoji} Trade {status_emoji}</b>

<b>Type:</b> {trade_type.upper()}
<b>Token:</b> {token_symbol}
<b>Amount:</b> {amount:.6f}
<b>Price:</b> {format_usd(price)}
<b>Value:</b> {format_usd(value_usd)}
<b>Status:</b> {status.upper()}
'''

    if signature:
      message += f'\n<b>Tx:</b> <code>{signature[:8]}...{signature[-8:]}</code>'

    message += f'\n\n⏰ {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")} UTC'

    return await self.send_message(message)

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

    message = f'''<b>{emoji} New Trading Signal</b>

<b>Action:</b> {action.upper()}
<b>Token:</b> {token_symbol}
<b>Strength:</b> {strength}
<b>Confidence:</b> {confidence:.0%}
<b>Risk:</b> {risk_level}
'''

    if entry_price:
      message += f'<b>Entry Price:</b> {format_usd(entry_price)}\n'

    # Truncate reasoning if too long
    max_reasoning_length = 200
    if len(reasoning) > max_reasoning_length:
      reasoning = reasoning[:max_reasoning_length] + '...'

    message += f'''
<b>Analysis:</b>
<i>{reasoning}</i>

⏰ {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")} UTC'''

    return await self.send_message(message)

  async def send_portfolio_update(
    self,
    total_value_usd: float,
    unrealized_pnl_usd: float,
    unrealized_pnl_percentage: float,
    position_count: int
  ) -> bool:
    """
    Send portfolio update notification.

    Args:
        total_value_usd: Total portfolio value
        unrealized_pnl_usd: Unrealized PnL in USD
        unrealized_pnl_percentage: Unrealized PnL percentage
        position_count: Number of open positions

    Returns:
        True if successful
    """
    pnl_emoji = '📈' if unrealized_pnl_usd >= 0 else '📉'
    pnl_color = 'green' if unrealized_pnl_usd >= 0 else 'red'

    message = f'''<b>💼 Portfolio Update</b>

<b>Total Value:</b> {format_usd(total_value_usd)}
<b>Unrealized PnL:</b> {pnl_emoji} {format_usd(unrealized_pnl_usd)} ({unrealized_pnl_percentage:+.2f}%)
<b>Open Positions:</b> {position_count}

⏰ {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")} UTC'''

    return await self.send_message(message)

  async def send_error_alert(
    self,
    error_type: str,
    error_message: str,
    context: Optional[str] = None
  ) -> bool:
    """
    Send error alert notification.

    Args:
        error_type: Type of error
        error_message: Error message
        context: Additional context

    Returns:
        True if successful
    """
    message = f'''<b>🚨 Error Alert</b>

<b>Type:</b> {error_type}
<b>Message:</b> {error_message}
'''

    if context:
      message += f'<b>Context:</b> {context}\n'

    message += f'\n⏰ {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")} UTC'

    return await self.send_message(message, disable_notification=False)

  async def send_daily_summary(
    self,
    total_trades: int,
    total_bought_usd: float,
    total_sold_usd: float,
    pnl_usd: float,
    best_trade: Optional[dict] = None,
    worst_trade: Optional[dict] = None
  ) -> bool:
    """
    Send daily trading summary.

    Args:
        total_trades: Number of trades
        total_bought_usd: Total bought value
        total_sold_usd: Total sold value
        pnl_usd: Net PnL
        best_trade: Best trade details
        worst_trade: Worst trade details

    Returns:
        True if successful
    """
    pnl_emoji = '📈' if pnl_usd >= 0 else '📉'

    message = f'''<b>📊 Daily Trading Summary</b>

<b>Total Trades:</b> {total_trades}
<b>Total Bought:</b> {format_usd(total_bought_usd)}
<b>Total Sold:</b> {format_usd(total_sold_usd)}
<b>Net PnL:</b> {pnl_emoji} {format_usd(pnl_usd)}
'''

    if best_trade:
      message += f'\n<b>✅ Best Trade:</b> {best_trade.get("token_symbol", "N/A")} +{format_usd(best_trade.get("pnl", 0))}'

    if worst_trade:
      message += f'\n<b>❌ Worst Trade:</b> {worst_trade.get("token_symbol", "N/A")} {format_usd(worst_trade.get("pnl", 0))}'

    message += f'\n\n⏰ {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")} UTC'

    return await self.send_message(message)

  async def test_connection(self) -> bool:
    """
    Test Telegram connection.

    Returns:
        True if connection successful
    """
    if not self.is_configured():
      logger.warning('Telegram not configured')
      return False

    message = '''<b>✅ Telegram Notification Test</b>

<b>System:</b> Solana AI Trader
<b>Status:</b> Connected successfully!

Your trading notifications will appear here.'''

    return await self.send_message(message)


# Global notifier instance
_telegram_notifier: Optional[TelegramNotifier] = None


def get_telegram_notifier() -> TelegramNotifier:
  """Get global Telegram notifier instance."""
  global _telegram_notifier
  if _telegram_notifier is None:
    _telegram_notifier = TelegramNotifier()
  return _telegram_notifier
