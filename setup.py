from web3 import Web3
import json

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

account = w3.eth.accounts[0]

with open("LibraryCore.json") as f:
    contract_data = json.load(f)

abi = contract_data["abi"]
bytecode = contract_data["bytecode"]

Library = w3.eth.contract(abi=abi, bytecode=bytecode)

tx_hash = Library.constructor().transact({"from": account})
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

contract_address = tx_receipt.contractAddress

print("Contract deployed at:", contract_address)

contract = w3.eth.contract(address=contract_address, abi=abi)

books = ["Math", "Physics", "AI", "Blockchain"]

for book in books:
    tx = contract.functions.addBook(book).transact({"from": account})
    w3.eth.wait_for_transaction_receipt(tx)

print("Fake books added successfully!")
