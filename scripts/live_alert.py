from web3 import Web3
import json
import time

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

with open("LibraryCore.json") as f:
    abi = json.load(f)["abi"]

contract = w3.eth.contract(
    address="PUT_ADDRESS_HERE",
    abi=abi
)

print("Listening for events...")

while True:
    events = contract.events.BookBorrowed.get_logs(fromBlock='latest')
    
    for event in events:
        print("ALERT: A book was borrowed!")

    events = contract.events.BookReturned.get_logs(fromBlock='latest')
    
    for event in events:
        print("ALERT: A book was returned!")

    time.sleep(5)
