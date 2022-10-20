import requests
import os
from typing import Any, Dict, List, Optional


class EtherscanClientException(Exception):
  pass


class Client:

  BASE_URL: str = 'https://api.etherscan.io/api'

  def __init__(self):
    self._api_key = os.getenv('ETHERSCAN_API_KEY')
  

  def get_contract_abi(self, contract_address: str) -> Optional[List[Any]]:
    url: str = (
      f"{self.BASE_URL}?"
      f"module=contract"
      f"&action=getabi"
      f"&address={contract_address}"
      f"&api_key={self._api_key}"
    )
    try: 
      response: str = requests.get(url)
      result: Dict[str, Any] = response.json()
    except:
      raise EtherscanClientException('Failed to fetch contract abi')

    if result['status'] == 0:
      return None

    return result['result']
