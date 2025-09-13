from web3 import Web3
import json

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

if w3.is_connected():
    print("Connected to Ganache!")
else:
    print("Failed to connect.")

# Load compiled contract
with open('build/compiled_contract.json', 'r') as file:
    compiled_sol = json.load(file)

abi = compiled_sol['contracts']['MyContract.sol']['MyContract']['abi']
contract_address = '0xe13Ce0C4979ADAD5EF3Fc75A8091A80eCF820FBE'  # Replace with your deployed address

# Create contract instance
contract = w3.eth.contract(address=contract_address, abi=abi)

# Set default account
w3.eth.default_account = w3.eth.accounts[0]

# Call registerUser
tx_hash = contract.functions.registerUser(w3.eth.default_account, "Alice").transact()
w3.eth.wait_for_transaction_receipt(tx_hash)
print("User registered!")

# Call getUser
name = contract.functions.getUser(w3.eth.default_account).call()
print(f"User name is: {name}")
