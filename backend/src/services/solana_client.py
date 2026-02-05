from solana.rpc.api import Client
from typing import Optional, Dict, Any
import httpx

from src.config import settings


class SolanaClient:
  """Solana RPC client wrapper."""

  def __init__(self, rpc_url: Optional[str] = None):
    """
    Initialize Solana client.

    Args:
        rpc_url: Solana RPC URL. If not provided, uses settings.
    """
    self.rpc_url = rpc_url or settings.helius_rpc_url or settings.solana_rpc_url
    self.client = Client(self.rpc_url)
    self.http_client = httpx.AsyncClient(timeout=30.0)

  async def close(self):
    """Close HTTP client."""
    await self.http_client.aclose()

  async def get_balance(self, wallet_address: str) -> float:
    """
    Get SOL balance for a wallet.

    Args:
        wallet_address: Wallet address

    Returns:
        Balance in SOL
    """
    response = await self.http_client.post(
      self.rpc_url,
      json={
        'jsonrpc': '2.0',
        'id': 1,
        'method': 'getBalance',
        'params': [wallet_address]
      }
    )
    data = response.json()
    if 'result' in data:
      # Convert lamports to SOL (1 SOL = 1,000,000,000 lamports)
      return data['result']['value'] / 1_000_000_000
    return 0.0

  async def get_token_balance(
    self,
    wallet_address: str,
    token_mint: str
  ) -> float:
    """
    Get token balance for a wallet.

    Args:
        wallet_address: Wallet address
        token_mint: Token mint address

    Returns:
        Token balance
    """
    response = await self.http_client.post(
      self.rpc_url,
      json={
        'jsonrpc': '2.0',
        'id': 1,
        'method': 'getTokenAccountsByOwner',
        'params': [
          wallet_address,
          {'mint': token_mint},
          {'encoding': 'jsonParsed'}
        ]
      }
    )
    data = response.json()
    if 'result' in data and data['result']['value']:
      # Get first token account balance
      account_data = data['result']['value'][0]['account']['data']['parsed']
      token_amount = account_data['info']['tokenAmount']
      return float(token_amount['amount']) / (10 ** token_amount['decimals'])
    return 0.0

  async def get_token_accounts(self, wallet_address: str) -> list[Dict[str, Any]]:
    """
    Get all token accounts for a wallet.

    Args:
        wallet_address: Wallet address

    Returns:
        List of token accounts
    """
    response = await self.http_client.post(
      self.rpc_url,
      json={
        'jsonrpc': '2.0',
        'id': 1,
        'method': 'getTokenAccountsByOwner',
        'params': [
          wallet_address,
          {'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA'},  # SPL Token Program
          {'encoding': 'jsonParsed'}
        ]
      }
    )
    data = response.json()
    accounts = []
    if 'result' in data:
      for account in data['result']['value']:
        account_data = account['account']['data']['parsed']['info']
        accounts.append({
          'mint': account_data['mint'],
          'amount': float(account_data['tokenAmount']['amount']),
          'decimals': account_data['tokenAmount']['decimals'],
          'symbol': account_data.get('tokenSymbol', 'UNKNOWN'),
        })
    return accounts

  async def get_transaction(self, signature: str) -> Optional[Dict[str, Any]]:
    """
    Get transaction details.

    Args:
        signature: Transaction signature

    Returns:
        Transaction details or None
    """
    try:
      response = await self.http_client.post(
        self.rpc_url,
        json={
          'jsonrpc': '2.0',
          'id': 1,
          'method': 'getTransaction',
          'params': [signature, {'encoding': 'jsonParsed'}]
        }
      )
      data = response.json()
      if 'result' in data:
        return data['result']
    except Exception as e:
      print(f'Error getting transaction: {e}')
    return None

  async def get_latest_blockhash(self) -> Optional[str]:
    """
    Get latest blockhash.

    Returns:
        Latest blockhash or None
    """
    try:
      response = await self.http_client.post(
        self.rpc_url,
        json={
          'jsonrpc': '2.0',
          'id': 1,
          'method': 'getLatestBlockhash',
          'params': [{'commitment': 'confirmed'}]
        }
      )
      data = response.json()
      if 'result' in data:
        return data['result']['value']['blockhash']
    except Exception as e:
      print(f'Error getting blockhash: {e}')
    return None

  async def send_transaction(self, transaction: str) -> Optional[str]:
    """
    Send signed transaction.

    Args:
        transaction: Base64 encoded transaction

    Returns:
        Transaction signature or None
    """
    try:
      response = await self.http_client.post(
        self.rpc_url,
        json={
          'jsonrpc': '2.0',
          'id': 1,
          'method': 'sendTransaction',
          'params': [
            transaction,
            {'encoding': 'base64', 'skipPreflight': False}
          ]
        }
      )
      data = response.json()
      if 'result' in data:
        return data['result']
    except Exception as e:
      print(f'Error sending transaction: {e}')
    return None


# Global client instance
_solana_client: Optional[SolanaClient] = None


def get_solana_client() -> SolanaClient:
  """Get global Solana client instance."""
  global _solana_client
  if _solana_client is None:
    _solana_client = SolanaClient()
  return _solana_client
