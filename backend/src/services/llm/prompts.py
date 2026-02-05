"""
Prompt templates for LLM-based trading analysis.
"""

TRADING_ANALYSIS_PROMPT = """You are an expert cryptocurrency trading analyst specializing in Solana tokens. Analyze the following market data and provide a trading recommendation.

## Token Information
- Symbol: {token_symbol}
- Current Price: ${current_price:.6f}
- 24h Volume: ${volume_24h:,.2f}
- 24h Price Change: {price_change_24h:+.2f}%
- Market Cap: {market_cap}
- Liquidity: {liquidity}

## Technical Indicators
```json
{technical_indicators}
```

## Additional Context
```json
{additional_context}
```

## Analysis Instructions

1. **Trend Analysis**: Evaluate the overall trend based on price action and technical indicators
2. **Momentum**: Assess momentum indicators (RSI, MACD) to determine strength
3. **Support/Resistance**: Identify key support and resistance levels
4. **Volume Analysis**: Consider trading volume and liquidity
5. **Risk Assessment**: Evaluate the risk level of trading this token

## Trading Guidelines

- Be conservative with new or low-liquidity tokens
- Prefer trades with strong technical confirmation
- Always consider risk/reward ratio
- Set appropriate stop losses (typically 5-15%)
- Set take profit targets (typically 10-30%)

## Required Output Format

Provide your analysis as a JSON object with these fields:

```json
{{
  "action": "buy | sell | hold",
  "strength": "very_weak | weak | moderate | strong | very_strong",
  "confidence": 0.0-1.0,
  "risk_level": "low | medium | high",
  "reasoning": "Your detailed analysis explaining the recommendation",
  "entry_price": null or suggested entry price,
  "stop_loss": null or suggested stop loss price,
  "take_profit": null or suggested take profit price,
  "position_size_percent": null or recommended position size as percentage of portfolio (1-5% typical)
}}
```

## Important Considerations

- If uncertainty is high, recommend "hold" with low confidence
- For low liquidity tokens, increase risk assessment
- Consider the overall market conditions
- Factor in the 24h price trend
- Use technical indicators to confirm decisions
- Be realistic about potential gains and losses

Provide ONLY the JSON object, no additional text.
"""


SENTIMENT_ANALYSIS_PROMPT = """Analyze the following social media posts and news headlines related to {token_symbol} cryptocurrency.

## Content to Analyze
{content}

## Analysis Instructions

1. **Overall Sentiment**: Determine if the sentiment is positive, negative, or neutral
2. **Key Themes**: Identify main topics discussed (technology, partnerships, price action, etc.)
3. **Sentiment Strength**: Rate how strong the sentiment is
4. **Credibility**: Assess the credibility of sources
5. **Market Impact**: Estimate potential market impact

## Required Output Format

```json
{{
  "overall_sentiment": "bullish | bearish | neutral",
  "sentiment_strength": "very_weak | weak | moderate | strong | very_strong",
  "confidence": 0.0-1.0,
  "key_themes": ["theme1", "theme2", ...],
  "credibility_score": 0.0-1.0,
  "market_impact": "low | medium | high",
  "reasoning": "Detailed explanation of the sentiment analysis"
}}
```

Provide ONLY the JSON object, no additional text.
"""


RISK_ASSESSMENT_PROMPT = """Assess the risk level of trading {token_symbol} based on the following data.

## Token Data
- Symbol: {token_symbol}
- Current Price: ${current_price}
- 24h Volume: ${volume_24h}
- Liquidity: ${liquidity}
- Market Cap: ${market_cap}
- Price Volatility: {volatility}%

## Holder Analysis
```json
{holder_data}
```

## Smart Contract Analysis
```json
{contract_data}
```

## Analysis Instructions

Evaluate the following risk factors:
1. **Liquidity Risk**: Can you exit the position quickly?
2. **Volatility Risk**: How much does price fluctuate?
3. **Concentration Risk**: Are holdings concentrated?
4. **Contract Risk**: Is the contract verified and safe?
5. **Market Risk**: Overall market conditions

## Required Output Format

```json
{{
  "overall_risk": "low | medium | high | very_high",
  "liquidity_risk": "low | medium | high",
  "volatility_risk": "low | medium | high",
  "contract_risk": "low | medium | high",
  "market_risk": "low | medium | high",
  "confidence": 0.0-1.0,
  "risk_factors": ["factor1", "factor2", ...],
  "recommendations": ["recommendation1", "recommendation2", ...],
  "max_position_size_percent": 1.0-10.0,
  "reasoning": "Detailed risk assessment explanation"
}}
```

Provide ONLY the JSON object, no additional text.
"""


PORTFOLIO_OPTIMIZATION_PROMPT = """Analyze the current portfolio and provide optimization recommendations.

## Current Portfolio
- Total Value: ${total_value}
- Available Balance: {available_balance} SOL
- Open Positions: {num_positions}
- Unrealized PnL: {unrealized_pnl}%

## Positions
```json
{positions}
```

## Market Conditions
```json
{market_conditions}
```

## Analysis Instructions

1. **Diversification**: Assess portfolio diversification
2. **Risk Exposure**: Evaluate overall risk exposure
3. **Performance**: Analyze individual position performance
4. **Rebalancing**: Identify positions that need adjustment
5. **Opportunities**: Suggest new opportunities

## Required Output Format

```json
{{
  "overall_health": "excellent | good | fair | poor",
  "diversification_score": 0.0-1.0,
  "risk_exposure": "low | medium | high",
  "recommendations": [
    {{
      "action": "buy | sell | hold | increase_position | decrease_position",
      "token_symbol": "SYMBOL",
      "reason": "Explanation",
      "priority": "low | medium | high"
    }}
  ],
  "positions_to_close": ["SYMBOL1", "SYMBOL2"],
  "new_opportunities": ["SYMBOL3", "SYMBOL4"],
  "portfolio_rebalance_percent": 0.0-100.0,
  "reasoning": "Detailed portfolio analysis"
}}
```

Provide ONLY the JSON object, no additional text.
"""
