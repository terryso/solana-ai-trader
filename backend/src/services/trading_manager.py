from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from src.config import settings
from src.utils import logger, format_sol, format_usd
from src.database import get_db, TradeRecord, SignalRecord
from src.models import Trade, TradeStatus, TradeType, Portfolio, Position
from src.services.trading_executor import get_trading_executor, TradingExecutor
from src.services.market_data import get_market_data_client, MarketDataClient
from src.services.notifications import get_telegram_notifier, get_discord_notifier


class TradingManager:
  """High-level trading orchestration service."""

  def __init__(
    self,
    executor: Optional[TradingExecutor] = None,
    market_client: Optional[MarketDataClient] = None
  ):
    """
    Initialize trading manager.

    Args:
        executor: Trading executor instance
        market_client: Market data client instance
    """
    self.executor = executor or get_trading_executor()
    self.market_client = market_client or get_market_data_client()
    self.telegram = get_telegram_notifier()
    self.discord = get_discord_notifier()

  async def execute_trade_with_validation(
    self,
    token_mint: str,
    token_symbol: str,
    amount_sol: float,
    trade_type: TradeType,
    slippage_percentage: float = 1.0
  ) -> Optional[Trade]:
    """
    Execute trade with full validation and risk checks.

    Args:
        token_mint: Token mint address
        token_symbol: Token symbol
        amount_sol: Amount in SOL
        trade_type: BUY or SELL
        slippage_percentage: Maximum slippage

    Returns:
        Trade record or None
    """
    try:
      # Validate trade
      is_valid, error_msg = await self.executor.validate_trade(amount_sol, token_mint)
      if not is_valid:
        logger.warning(f'Trade validation failed: {error_msg}')
        return None

      # Execute trade
      if trade_type == TradeType.BUY:
        result = await self.executor.execute_buy(
          token_mint=token_mint,
          token_symbol=token_symbol,
          amount_sol=amount_sol,
          slippage_percentage=slippage_percentage
        )
      else:
        result = await self.executor.execute_sell(
          token_mint=token_mint,
          token_symbol=token_symbol,
          amount_tokens=amount_sol,  # Reusing same parameter
          slippage_percentage=slippage_percentage
        )

      if not result.success:
        logger.error(f'Trade execution failed: {result.error}')
        return None

      # Save to database
      if result.trade:
        self._save_trade_to_db(result.trade)
        logger.info(
          f'Trade executed: {trade_type.value} {token_symbol} '
          f'Amount: {amount_sol} SOL'
        )

        # Send notifications
        if self.telegram.is_configured():
          await self.telegram.send_trade_notification(
            trade_type=trade_type.value,
            token_symbol=token_symbol,
            amount=result.trade.amount,
            price=result.trade.price,
            value_usd=result.trade.value_usd,
            status=result.trade.status.value,
            signature=result.trade.signature
          )

        if self.discord.is_configured():
          await self.discord.send_trade_notification(
            trade_type=trade_type.value,
            token_symbol=token_symbol,
            amount=result.trade.amount,
            price=result.trade.price,
            value_usd=result.trade.value_usd,
            status=result.trade.status.value,
            signature=result.trade.signature
          )

      return result.trade

    except Exception as e:
      logger.error(f'Error in execute_trade_with_validation: {e}')
      return None

  def _save_trade_to_db(self, trade: Trade) -> int:
    """
    Save trade to database.

    Args:
        trade: Trade object

    Returns:
        Trade ID
    """
    try:
      db: Session = next(get_db())
      record = TradeRecord(
        trade_type=trade.trade_type.value,
        token_address=trade.token_address,
        token_symbol=trade.token_symbol,
        amount=trade.amount,
        price=trade.price,
        value_usd=trade.value_usd,
        status=trade.status.value,
        signature=trade.signature,
        signal_id=trade.signal_id,
        timestamp=trade.timestamp,
        executed_at=trade.executed_at,
        error_message=trade.error_message
      )
      db.add(record)
      db.commit()
      db.refresh(record)
      return record.id
    except Exception as e:
      logger.error(f'Error saving trade to database: {e}')
      return 0

  def get_open_positions(self) -> List[Dict[str, Any]]:
    """
    Get current open positions.

    Returns:
        List of open positions
    """
    try:
      db: Session = next(get_db())

      # Get recent buy trades without corresponding sells
      # This is simplified - in production you'd track positions properly
      recent_buys = db.query(TradeRecord).filter(
        TradeRecord.trade_type == 'buy',
        TradeRecord.status == 'executed'
      ).order_by(TradeRecord.timestamp.desc()).limit(10).all()

      positions = []
      for trade in recent_buys:
        positions.append({
          'token_address': trade.token_address,
          'token_symbol': trade.token_symbol,
          'amount': trade.amount,
          'entry_price': trade.price,
          'value_usd': trade.value_usd,
          'opened_at': trade.timestamp
        })

      return positions

    except Exception as e:
      logger.error(f'Error getting open positions: {e}')
      return []

  async def get_portfolio_value(self) -> Optional[Portfolio]:
    """
    Get current portfolio value and positions.

    Returns:
        Portfolio object or None
    """
    try:
      # Get SOL balance
      sol_balance = await self.executor.get_wallet_balance()

      # Get SOL price in USD
      sol_price = await self.market_client.get_sol_price()

      positions = []
      total_value_usd = sol_balance * sol_price

      # Get token positions
      wallet_address = await self.executor.get_wallet_address()
      if wallet_address:
        open_positions = self.get_open_positions()

        for pos in open_positions:
          current_price = await self.market_client.get_token_price(pos['token_address'])
          if current_price:
            pnl = (current_price - pos['entry_price']) * pos['amount']
            pnl_pct = ((current_price - pos['entry_price']) / pos['entry_price']) * 100

            positions.append(Position(
              token_address=pos['token_address'],
              token_symbol=pos['token_symbol'],
              amount=pos['amount'],
              average_entry_price=pos['entry_price'],
              current_price=current_price,
              value_usd=pos['amount'] * current_price,
              pnl_usd=pnl,
              pnl_percentage=pnl_pct,
              opened_at=pos['opened_at']
            ))

            total_value_usd += positions[-1].value_usd

      # Calculate total PnL
      unrealized_pnl_usd = sum(p.pnl_usd for p in positions)
      unrealized_pnl_pct = (unrealized_pnl_usd / total_value_usd * 100) if total_value_usd > 0 else 0

      return Portfolio(
        total_value_usd=total_value_usd,
        available_balance_sol=sol_balance,
        positions=positions,
        unrealized_pnl_usd=unrealized_pnl_usd,
        unrealized_pnl_percentage=unrealized_pnl_pct
      )

    except Exception as e:
      logger.error(f'Error getting portfolio value: {e}')
      return None

  def get_trade_history(
    self,
    limit: int = 100,
    token_address: Optional[str] = None
  ) -> List[Dict[str, Any]]:
    """
    Get trade history.

    Args:
        limit: Maximum number of trades
        token_address: Filter by token address

    Returns:
        List of trades
    """
    try:
      db: Session = next(get_db())
      query = db.query(TradeRecord)

      if token_address:
        query = query.filter(TradeRecord.token_address == token_address)

      trades = query.order_by(
        TradeRecord.timestamp.desc()
      ).limit(limit).all()

      return [
        {
          'id': t.id,
          'type': t.trade_type,
          'token_address': t.token_address,
          'token_symbol': t.token_symbol,
          'amount': t.amount,
          'price': t.price,
          'value_usd': t.value_usd,
          'status': t.status,
          'signature': t.signature,
          'timestamp': t.timestamp,
          'executed_at': t.executed_at,
        }
        for t in trades
      ]

    except Exception as e:
      logger.error(f'Error getting trade history: {e}')
      return []

  def get_daily_pnl(self) -> Dict[str, float]:
    """
    Calculate daily PnL.

    Returns:
        PnL statistics
    """
    try:
      db: Session = next(get_db())

      # Get today's trades
      today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

      trades = db.query(TradeRecord).filter(
        TradeRecord.timestamp >= today,
        TradeRecord.status == 'executed'
      ).all()

      total_bought = sum(t.value_usd for t in trades if t.trade_type == 'buy')
      total_sold = sum(t.value_usd for t in trades if t.trade_type == 'sell')

      pnl = total_sold - total_bought

      return {
        'total_bought_usd': total_bought,
        'total_sold_usd': total_sold,
        'pnl_usd': pnl,
        'trade_count': len(trades)
      }

    except Exception as e:
      logger.error(f'Error calculating daily PnL: {e}')
      return {
        'total_bought_usd': 0.0,
        'total_sold_usd': 0.0,
        'pnl_usd': 0.0,
        'trade_count': 0
      }

  def should_stop_trading(self) -> bool:
    """
    Check if should stop trading based on daily loss limit.

    Returns:
        True if should stop trading
    """
    daily_stats = self.get_daily_pnl()
    max_loss_usd = 0  # Would calculate from portfolio value and max_daily_loss setting

    if daily_stats['pnl_usd'] < -abs(max_loss_usd):
      logger.warning(
        f'Daily loss limit reached: {format_usd(daily_stats["pnl_usd"])}. '
        'Trading halted.'
      )
      return True

    return False


# Global manager instance
_trading_manager: Optional[TradingManager] = None


def get_trading_manager() -> TradingManager:
  """Get global trading manager instance."""
  global _trading_manager
  if _trading_manager is None:
    _trading_manager = TradingManager()
  return _trading_manager
