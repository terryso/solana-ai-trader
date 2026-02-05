import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class IndicatorResult:
  """Result of technical indicator calculation."""
  name: str
  value: float
  signal: str  # bullish, bearish, neutral
  confidence: float  # 0.0 to 1.0


class TechnicalIndicators:
  """Calculate technical indicators for price data."""

  @staticmethod
  def sma(prices: List[float], period: int) -> Optional[float]:
    """
    Calculate Simple Moving Average.

    Args:
        prices: List of prices
        period: Period for SMA

    Returns:
        SMA value or None
    """
    if len(prices) < period:
      return None
    return sum(prices[-period:]) / period

  @staticmethod
  def ema(prices: List[float], period: int) -> Optional[float]:
    """
    Calculate Exponential Moving Average.

    Args:
        prices: List of prices
        period: Period for EMA

    Returns:
        EMA value or None
    """
    if len(prices) < period:
      return None

    multiplier = 2 / (period + 1)
    ema = prices[0]

    for price in prices[1:]:
      ema = (price - ema) * multiplier + ema

    return ema

  @staticmethod
  def rsi(prices: List[float], period: int = 14) -> Optional[float]:
    """
    Calculate Relative Strength Index.

    Args:
        prices: List of prices
        period: Period for RSI (default 14)

    Returns:
        RSI value (0-100) or None
    """
    if len(prices) < period + 1:
      return None

    # Calculate price changes
    price_changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]

    # Separate gains and losses
    gains = [max(change, 0) for change in price_changes]
    losses = [abs(min(change, 0)) for change in price_changes]

    # Calculate average gains and losses
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period

    if avg_loss == 0:
      return 100.0

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi

  @staticmethod
  def macd(
    prices: List[float],
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9
  ) -> Optional[Dict[str, float]]:
    """
    Calculate MACD (Moving Average Convergence Divergence).

    Args:
        prices: List of prices
        fast_period: Fast EMA period (default 12)
        slow_period: Slow EMA period (default 26)
        signal_period: Signal line period (default 9)

    Returns:
        Dictionary with macd, signal, and histogram values
    """
    if len(prices) < slow_period:
      return None

    # Calculate EMAs
    fast_ema = TechnicalIndicators.ema(prices, fast_period)
    slow_ema = TechnicalIndicators.ema(prices, slow_period)

    if fast_ema is None or slow_ema is None:
      return None

    macd_line = fast_ema - slow_ema

    # For simplicity, we'll return the current MACD value
    # In a full implementation, you'd calculate the signal line from MACD history
    return {
      'macd': macd_line,
      'signal': macd_line * 0.9,  # Simplified
      'histogram': macd_line * 0.1  # Simplified
    }

  @staticmethod
  def bollinger_bands(
    prices: List[float],
    period: int = 20,
    num_std: float = 2.0
  ) -> Optional[Dict[str, float]]:
    """
    Calculate Bollinger Bands.

    Args:
        prices: List of prices
        period: Period for SMA (default 20)
        num_std: Number of standard deviations (default 2)

    Returns:
        Dictionary with upper, middle, and lower bands
    """
    if len(prices) < period:
      return None

    recent_prices = prices[-period:]
    sma = sum(recent_prices) / period
    std = np.std(recent_prices)

    return {
      'upper': sma + (num_std * std),
      'middle': sma,
      'lower': sma - (num_std * std),
      'bandwidth': (num_std * std * 2) / sma if sma > 0 else 0
    }

  @staticmethod
  def stochastic(
    high_prices: List[float],
    low_prices: List[float],
    close_prices: List[float],
    period: int = 14
  ) -> Optional[Dict[str, float]]:
    """
    Calculate Stochastic Oscillator.

    Args:
        high_prices: List of high prices
        low_prices: List of low prices
        close_prices: List of close prices
        period: Period for calculation (default 14)

    Returns:
        Dictionary with %K and %D values
    """
    if len(close_prices) < period:
      return None

    recent_highs = high_prices[-period:]
    recent_lows = low_prices[-period:]

    highest_high = max(recent_highs)
    lowest_low = min(recent_lows)

    if highest_high == lowest_low:
      return None

    current_close = close_prices[-1]
    k = ((current_close - lowest_low) / (highest_high - lowest_low)) * 100

    # For simplicity, %D is a smoothed version of %K
    d = k * 0.9  # Simplified

    return {
      'k': k,
      'd': d
    }

  @staticmethod
  def calculate_volatility(prices: List[float], period: int = 20) -> Optional[float]:
    """
    Calculate price volatility (standard deviation).

    Args:
        prices: List of prices
        period: Period for calculation

    Returns:
        Volatility as percentage or None
    """
    if len(prices) < period:
      return None

    recent_prices = prices[-period:]
    returns = [(recent_prices[i] - recent_prices[i-1]) / recent_prices[i-1]
                for i in range(1, len(recent_prices))]

    volatility = np.std(returns) * np.sqrt(252) * 100  # Annualized volatility
    return volatility

  @staticmethod
  def analyze_trend(prices: List[float]) -> Dict[str, Any]:
    """
    Analyze overall trend.

    Args:
        prices: List of prices

    Returns:
        Trend analysis dictionary
    """
    if len(prices) < 10:
      return {
        'trend': 'unknown',
        'strength': 'unknown',
        'direction': 0
      }

    # Calculate short and long EMAs
    short_ema = TechnicalIndicators.ema(prices, 10)
    long_ema = TechnicalIndicators.ema(prices, 30)

    if short_ema is None or long_ema is None:
      return {
        'trend': 'unknown',
        'strength': 'unknown',
        'direction': 0
      }

    # Determine trend direction
    if short_ema > long_ema:
      trend = 'uptrend'
      direction = 1
    elif short_ema < long_ema:
      trend = 'downtrend'
      direction = -1
    else:
      trend = 'sideways'
      direction = 0

    # Calculate trend strength based on EMA separation
    strength = abs(short_ema - long_ema) / long_ema * 100

    if strength > 2:
      strength_level = 'strong'
    elif strength > 1:
      strength_level = 'moderate'
    else:
      strength_level = 'weak'

    return {
      'trend': trend,
      'strength': strength_level,
      'direction': direction,
      'ema_separation_percent': strength
    }

  @staticmethod
  def get_support_resistance(
    prices: List[float],
    window: int = 5
  ) -> Dict[str, List[float]]:
    """
    Identify support and resistance levels.

    Args:
        prices: List of prices
        window: Window size for finding local extrema

    Returns:
        Dictionary with support and resistance levels
    """
    if len(prices) < window * 2:
      return {
        'support': [],
        'resistance': []
      }

    supports = []
    resistances = []

    # Find local minima (support) and maxima (resistance)
    for i in range(window, len(prices) - window):
      local_min = True
      local_max = True

      for j in range(i - window, i + window + 1):
        if j == i:
          continue
        if prices[j] < prices[i]:
          local_min = False
        if prices[j] > prices[i]:
          local_max = False

      if local_min:
        supports.append(prices[i])
      if local_max:
        resistances.append(prices[i])

    # Remove duplicates (within 1% tolerance)
    def filter_levels(levels: List[float]) -> List[float]:
      if not levels:
        return []

      filtered = [levels[0]]
      for level in levels[1:]:
        if not any(abs(level - existing) / existing < 0.01 for existing in filtered):
          filtered.append(level)
      return filtered

    return {
      'support': sorted(filter_levels(supports))[-3:],  # Top 3 recent supports
      'resistance': sorted(filter_levels(resistances))[-3:]  # Top 3 recent resistances
    }


def analyze_price_history(
  price_history: List[Dict[str, Any]]
) -> Dict[str, Any]:
  """
  Analyze price history and calculate all technical indicators.

  Args:
      price_history: List of price data dictionaries with 'price', 'high', 'low', 'timestamp'

  Returns:
      Dictionary with all technical indicators
  """
  if not price_history or len(price_history) < 2:
    return {}

  # Extract price data
  prices = [p['price'] for p in price_history]
  high_prices = [p.get('high', p['price']) for p in price_history]
  low_prices = [p.get('low', p['price']) for p in price_history]

  indicators = {}

  # Moving averages
  indicators['sma_20'] = TechnicalIndicators.sma(prices, 20)
  indicators['sma_50'] = TechnicalIndicators.sma(prices, 50)
  indicators['ema_12'] = TechnicalIndicators.ema(prices, 12)
  indicators['ema_26'] = TechnicalIndicators.ema(prices, 26)

  # RSI
  rsi = TechnicalIndicators.rsi(prices, 14)
  if rsi is not None:
    indicators['rsi'] = rsi
    # RSI signal
    if rsi > 70:
      indicators['rsi_signal'] = 'overbought'
    elif rsi < 30:
      indicators['rsi_signal'] = 'oversold'
    else:
      indicators['rsi_signal'] = 'neutral'

  # MACD
  macd = TechnicalIndicators.macd(prices)
  if macd:
    indicators['macd'] = macd

  # Bollinger Bands
  bb = TechnicalIndicators.bollinger_bands(prices)
  if bb:
    indicators['bollinger_bands'] = bb

    # Bollinger Bands position
    current_price = prices[-1]
    if current_price > bb['upper']:
      indicators['bb_position'] = 'above_upper'
    elif current_price < bb['lower']:
      indicators['bb_position'] = 'below_lower'
    else:
      indicators['bb_position'] = 'within_bands'

  # Stochastic
  stoch = TechnicalIndicators.stochastic(high_prices, low_prices, prices)
  if stoch:
    indicators['stochastic'] = stoch

  # Volatility
  volatility = TechnicalIndicators.calculate_volatility(prices)
  if volatility is not None:
    indicators['volatility_annualized'] = volatility

  # Trend analysis
  trend = TechnicalIndicators.analyze_trend(prices)
  indicators['trend'] = trend

  # Support and resistance
  sr = TechnicalIndicators.get_support_resistance(prices)
  indicators['support_resistance'] = sr

  return indicators
