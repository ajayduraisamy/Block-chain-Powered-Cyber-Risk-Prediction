from solcx import compile_standard, install_solc
import json
import os 

# Install Solidity compiler version
install_solc('0.8.0')

# Read the Solidity contract
with open('contracts/MyContract.sol', 'r') as file:
    source_code = file.read()

compiled_sol = compile_standard({
    "language": "Solidity",
    "sources": {
        "MyContract.sol": {
            "content": source_code
        }
    },
    "settings": {
        "outputSelection": {
            "*": {
                "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
            }
        }
    }
}, solc_version="0.8.0")

# Create 'build' directory if it doesn't exist
if not os.path.exists('build'):
    os.makedirs('build')

# Save compiled output
with open('build/compiled_contract.json', 'w') as f:
    json.dump(compiled_sol, f, indent=4)

# Extract ABI and bytecode
abi = compiled_sol['contracts']['MyContract.sol']['MyContract']['abi']
bytecode = compiled_sol['contracts']['MyContract.sol']['MyContract']['evm']['bytecode']['object']

print("Contract ABI and bytecode compiled successfully!")
