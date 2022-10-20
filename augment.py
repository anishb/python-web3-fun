import os
from etherscan import Client
from dotenv import load_dotenv
from constants import UNISWAP_QUOTER_ADDRESS

load_dotenv()
es: Client = Client()
abi = es.get_contract_abi(UNISWAP_QUOTER_ADDRESS)
print(abi)
