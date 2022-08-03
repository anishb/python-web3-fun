import os
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from eth_account.messages import encode_defunct
from dotenv import load_dotenv


class Web3Playground:

  web3: Web3
  account1_private_key: str
  account1: Account
  account2: Account

  def __init__(self):
    self.web3 = Web3(Web3.HTTPProvider(os.getenv('ETHEREUM_GOERLI_ENDPOINT')))
    self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    assert self.web3.isConnected(), 'Could not connect to node'
    
    self.account1_private_key = os.getenv('ACCT1_PRIVATE_KEY')
    self.account1 = Account.from_key(self.account1_private_key)
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
      self.account1_private_key 
    )
    tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)

    return self.web3.toHex(tx_hash)

  def sign_message(self, message: str):
    signable_message = encode_defunct(text=message)
    signed_message = self.web3.eth.account.sign_message(
      signable_message,
      private_key=self.account1_private_key
    )
    return signed_message

  def verify_message(self, message: str, signed_message) -> bool:
    signable_message = encode_defunct(text=message)
    return self.web3.eth.account.recover_message(
      signable_message,
      signature=signed_message.signature
    )

        


if __name__ == "__main__":
  load_dotenv()
  playground: Web3Playground = Web3Playground()

  # Send some eth
  playground.print_balances()
  #tx_hash = playground.send_some_eth()
  #print(tx_hash)
  #playground.print_balances


  # Sign and verify a message signature
  message: str = "Me gusta Miami"
  signed_message = playground.sign_message(message)
  assert playground.verify_message(message, signed_message), 'message could not be verified'
