from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/e7ad77c7a4eb4a76a9c4f228c843d59c'))

print(w3.is_connected())  # Should print True if connection works
