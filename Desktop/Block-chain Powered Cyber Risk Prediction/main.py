from web3 import Web3

# Connect to Ganache local blockchain
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

# Check if connected
print("Connected:", w3.is_connected())

if w3.is_connected():
    # Get list of accounts
    accounts = w3.eth.accounts
    print("Accounts:", accounts)

    # Get balance of the first account
    balance = w3.eth.get_balance(accounts[0])
    print("Balance of first account:", w3.from_wei(balance, 'ether'), "ETH")

    # Send 1 ETH from first account to second account as a test transaction
    tx_hash = w3.eth.send_transaction({
        'from': accounts[0],
        'to': accounts[1],
        'value': w3.to_wei(1, 'ether')
    })

    print("Transaction sent! Hash:", tx_hash.hex())

    # Wait for transaction receipt
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print("Transaction mined in block:", receipt.blockNumber)

    # Show new balances
    balance_0 = w3.eth.get_balance(accounts[0])
    balance_1 = w3.eth.get_balance(accounts[1])
    print("New balance of account 0:", w3.from_wei(balance_0, 'ether'), "ETH")
    print("New balance of account 1:", w3.from_wei(balance_1, 'ether'), "ETH")
