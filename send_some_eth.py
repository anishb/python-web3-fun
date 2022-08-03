import os
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from eth_account.signers.local import LocalAccount
from dotenv import load_dotenv


class Web3Playground:

  web3: Web3
  account1: Account
  account2: Account

  def __init__(self):
    self.web3 = Web3(Web3.HTTPProvider(os.getenv('ETHEREUM_GOERLI_ENDPOINT')))
    self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    assert self.web3.isConnected(), 'Could not connect to node'
    
    self.account1 = Account.from_key(os.getenv('ACCT1_PRIVATE_KEY'))
    self.account2 = Account.from_key(os.getenv('ACCT2_PRIVATE_KEY'))

  def print_balances(self) -> None:
    account1_balance: int = self.web3.fromWei(
        self.web3.eth.get_balance(
          self.account1.address
        ),
        'ether'
    )
    print("%s %f ether" % (self.account1.address, account1_balance))

    account2_balance: int = self.web3.fromWei(
        self.web3.eth.get_balance(
          self.account2.address
        ),
        'ether'
    )
    print("%s %f ether" % (self.account2.address, account2_balance))

  def send_some_eth(self) -> str:
    nonce = self.web3.eth.get_transaction_count(self.account1.address)
    tx = {
      'from': self.account1.address,
      'to': self.account2.address,
      'value': self.web3.toWei('0.0001', 'ether'),
      'nonce': nonce,
      'gas': 21000,
      'maxFeePerGas': 2,
      'maxPriorityFeePerGas': 2,
      'chainId': 5
    }
    signed_tx = self.web3.eth.account.sign_transaction(
      tx,
      os.getenv('ACCT1_PRIVATE_KEY') 
    )
    tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)

    return self.web3.toHex(tx_hash)

  def signed_message(self) -> str:
    pass


if __name__ == "__main__":
  load_dotenv()
  playground = Web3Playground()
  playground.print_balances()
  #tx_hash = playground.send_some_eth()
  #print(tx_hash)
  #playground.print_balances
  