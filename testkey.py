from eth_account import Account
from web3 import Web3
import json
backend_private_key = "0xb70168b6e74d4b332733b10a895ab7d14a0b735c3fef4cd55172de6864d07df3"
backend_account = Account.from_key(backend_private_key)

# Initialize Web3 connection (example uses local Ganache, change as needed)
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

# Check balance
balance = w3.eth.get_balance(backend_account.address)
print("Backend balance:", w3.from_wei(balance, 'ether'), "ETH")  # Should show 1000 ETH
