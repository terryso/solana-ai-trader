from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime

from src.services import (
  get_trading_manager,
  get_signal_service,
  get_market_data_client
)
from src.utils import logger

router = APIRouter()


@router.get('/api/portfolio')
async def get_portfolio():
  """Get current portfolio value and positions."""
  try:
    manager = get_trading_manager()
    portfolio = await manager.get_portfolio_value()

    if not portfolio:
      raise HTTPException(status_code=404, detail='Portfolio not found')

    return {
      'total_value_usd': portfolio.total_value_usd,
      'available_balance_sol': portfolio.available_balance_sol,
      'unrealized_pnl_usd': portfolio.unrealized_pnl_usd,
      'unrealized_pnl_percentage': portfolio.unrealized_pnl_percentage,
      'positions': [
        {
          'token_address': p.token_address,
          'token_symbol': p.token_symbol,
          'amount': p.amount,
          'average_entry_price': p.average_entry_price,
          'current_price': p.current_price,
          'value_usd': p.value_usd,
          'pnl_usd': p.pnl_usd,
          'pnl_percentage': p.pnl_percentage,
          'opened_at': p.opened_at.isoformat()
        }
        for p in portfolio.positions
      ],
      'timestamp': datetime.utcnow().isoformat()
    }

  except Exception as e:
    logger.error(f'Error fetching portfolio: {e}')
    raise HTTPException(status_code=500, detail=str(e))


@router.get('/api/trades')
async def get_trades(
  limit: int = 100,
  token_address: Optional[str] = None
):
  """Get trade history."""
  try:
    manager = get_trading_manager()
    trades = manager.get_trade_history(limit=limit, token_address=token_address)

    return {
      'trades': trades,
      'count': len(trades)
    }

  except Exception as e:
    logger.error(f'Error fetching trades: {e}')
    raise HTTPException(status_code=500, detail=str(e))


@router.get('/api/signals')
async def get_signals(
  limit: int = 50,
  token_address: Optional[str] = None
):
  """Get trading signals."""
  try:
    signal_service = get_signal_service()
    signals = signal_service.get_recent_signals(
      token_address=token_address,
      limit=limit
    )

    return {
      'signals': signals,
      'count': len(signals)
    }

  except Exception as e:
    logger.error(f'Error fetching signals: {e}')
    raise HTTPException(status_code=500, detail=str(e))


@router.get('/api/daily-pnl')
async def get_daily_pnl():
  """Get daily PnL statistics."""
  try:
    manager = get_trading_manager()
    pnl = manager.get_daily_pnl()

    return pnl

  except Exception as e:
    logger.error(f'Error fetching daily PnL: {e}')
    raise HTTPException(status_code=500, detail=str(e))


@router.get('/api/market/{token_address}')
async def get_market_data(token_address: str):
  """Get market data for a token."""
  try:
    client = get_market_data_client()
    price = await client.get_token_price(token_address)

    if price is None:
      raise HTTPException(status_code=404, detail='Token not found')

    return {
      'token_address': token_address,
      'price': price,
      'timestamp': datetime.utcnow().isoformat()
    }

  except Exception as e:
    logger.error(f'Error fetching market data: {e}')
    raise HTTPException(status_code=500, detail=str(e))


@router.get('/api/stats')
async def get_stats():
  """Get overall trading statistics."""
  try:
    manager = get_trading_manager()
    signal_service = get_signal_service()

    # Get portfolio
    portfolio = await manager.get_portfolio_value()

    # Get daily PnL
    daily_pnl = manager.get_daily_pnl()

    # Get recent signals
    recent_signals = signal_service.get_recent_signals(limit=10)

    # Get recent trades
    recent_trades = manager.get_trade_history(limit=10)

    # Calculate stats
    total_signals = len(recent_signals)
    buy_signals = sum(1 for s in recent_signals if s['action'] == 'buy')
    sell_signals = sum(1 for s in recent_signals if s['action'] == 'sell')

    return {
      'portfolio': {
        'total_value_usd': portfolio.total_value_usd if portfolio else 0,
        'available_balance_sol': portfolio.available_balance_sol if portfolio else 0,
        'unrealized_pnl_usd': portfolio.unrealized_pnl_usd if portfolio else 0,
        'unrealized_pnl_percentage': portfolio.unrealized_pnl_percentage if portfolio else 0,
        'position_count': len(portfolio.positions) if portfolio else 0
      },
      'daily': {
        'total_bought_usd': daily_pnl['total_bought_usd'],
        'total_sold_usd': daily_pnl['total_sold_usd'],
        'pnl_usd': daily_pnl['pnl_usd'],
        'trade_count': daily_pnl['trade_count']
      },
      'signals': {
        'total': total_signals,
        'buy': buy_signals,
        'sell': sell_signals,
        'hold': total_signals - buy_signals - sell_signals
      },
      'trades': {
        'recent_count': len(recent_trades)
      },
      'timestamp': datetime.utcnow().isoformat()
    }

  except Exception as e:
    logger.error(f'Error fetching stats: {e}')
    raise HTTPException(status_code=500, detail=str(e))


@router.get('/api/health')
async def health_check():
  """Health check endpoint."""
  return {
    'status': 'healthy',
    'timestamp': datetime.utcnow().isoformat()
  }
