from web3 import Web3
import json

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

# accounts
admin = w3.eth.accounts[0]
user = w3.eth.accounts[1]

# load ABI
with open("LibraryCore.json") as f:
    abi = json.load(f)["abi"]

#  address لما يتوفر
contract = w3.eth.contract(
    address="PUT_ADDRESS_HERE",
    abi=abi
)

# test
def test_non_admin_cannot_add_book():
    try:
        contract.functions.addBook("Hacked Book").transact({'from': user})
        print("❌ Test Failed: User added a book!")
    except:
        print("✅ Test Passed: User cannot add book")

test_non_admin_cannot_add_book()
