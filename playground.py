import os
from datetime import datetime
from typing import Dict, Any
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from eth_account.messages import encode_defunct
from dotenv import load_dotenv
from enum import Enum
from constants import DAI_CONTRACT_ADDRESS, DAI_ABI, GREETING_CONTRACT_ADDRESS,\
   GREETING_ABI


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

  def read_smart_contract(self) -> None:
    contract = self.web3.eth.contract(
      address=Web3.toChecksumAddress(DAI_CONTRACT_ADDRESS),
      abi=DAI_ABI
    )
  
    total_supply: float = contract.functions.totalSupply().call()
    name: str = contract.functions.name().call()
    symbol: str = contract.functions.symbol().call()
    wallet_address: str = Web3.toChecksumAddress('0x2a098157953d0e0108447e27ec5d4fa971fd54cb')
    balance: float = contract.functions.balanceOf(wallet_address).call()

    print("Total Supply = %.2f %s" % (self.web3.fromWei(total_supply, 'ether'), symbol))
    print("Token Name = %s" % name)
    print("Balance of wallet %s = %.2f %s" % (wallet_address, self.web3.fromWei(balance, 'ether'), symbol))

  def get_greeting(self) -> str:
    contract = self.web3.eth.contract(
      address=Web3.toChecksumAddress(GREETING_CONTRACT_ADDRESS),
      abi=GREETING_ABI
    )
    greeting: str = contract.functions.greet().call()
    return greeting

  def set_greeting(self, new_greeting: str) -> str:
    contract = self.web3.eth.contract(
      address=Web3.toChecksumAddress(GREETING_CONTRACT_ADDRESS),
      abi=GREETING_ABI
    )
    nonce = self.web3.eth.get_transaction_count(self.account1.address)
    tx = contract.functions.setGreeting(new_greeting).build_transaction({
      'nonce': nonce,
      'gas': 70000,
      'maxFeePerGas': self.web3.toWei('2', 'gwei'),
      'maxPriorityFeePerGas': self.web3.toWei('1', 'gwei'),
      'chainId': 5
    })
    signed_tx = self.web3.eth.account.sign_transaction(
      tx,
      self.account1_private_key 
    )
    tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    self.web3.eth.waitForTransactionReceipt(tx_hash)

    return self.web3.toHex(tx_hash)

  def read_blocks(self) -> None:
    latest_block: Dict[str, Any] = self.web3.eth.get_block('latest')
    block_number: int = latest_block['number']
    block_hash: str = latest_block['hash'].hex()
    parent_hash: str = latest_block['parentHash'].hex()
    num_transactions: int = len(latest_block['transactions'])
    block_time: datetime = datetime.fromtimestamp(latest_block['timestamp'])

    print("Latest block number = %d" % block_number)
    print("Block hash = %s" % block_hash)
    print("Parent block hash = %s" % parent_hash)
    print("Number of transactions = %d" % num_transactions)
    print("Block time = %s" % block_time.strftime("%m/%d/%Y, %H:%M:%S"))

    for i in range(num_transactions):
      self.read_transaction(block_number, i)

  def read_transaction(self, block_number: int, tx_index: int) -> None:
    tx_obj: Dict[str, Any] = self.web3.eth.get_transaction_by_block(block_number, tx_index)
    tx_hash: str = tx_obj['hash'].hex()
    tx_index: int = tx_obj['transactionIndex']
    tx_from: str = tx_obj['from']
    tx_to: str = tx_obj['to'] if tx_obj['to'] else None
    tx_value: int = tx_obj['value']
    tx_input: str = tx_obj['input'] if tx_obj['input'] else None

    print("==========================================================")
    print("Transaction Hash = %s" % tx_hash)
    print("Transaction Index = %d" % tx_index)

    print("From = %s" % tx_from)
    if tx_from is not None:
      if self.is_contract_address(tx_from):
        print("Sender is a contract")
      else:
        print("Sender is an externally owned account")
    
    print("To = %s" % tx_to)
    if tx_to is not None:
      if self.is_contract_address(tx_to):
        print("Receiver is a contract")
      else:
        print("Receiver is an externally owned account")

    print("Value = %.4f gwei" % self.web3.fromWei(tx_value, 'gwei'))

  def is_contract_address(self, tx_hash: str) -> bool:
    result: bytes = self.web3.eth.getCode(tx_hash)
    contract_data: str = result.hex()
    if contract_data == '0x':
        return False
    return True


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

  # Read some data from Dai smart contract
  playground.read_smart_contract()

  # Interact with greeter contract
  print("Current greeting = %s" % playground.get_greeting())
  #tx_hash = playground.set_greeting('Hola!')
  #print("Set new greeting. TX hash = %s" % tx_hash)
  #print("New greeting = %s" % playground.get_greeting())

  # Read block data
  playground.read_blocks()

  # Check is address is a contract
  assert playground.is_contract_address(DAI_CONTRACT_ADDRESS), 'Should be DAI address'

