from web3 import Web3
import json

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

with open("LibraryCore.json") as f:
    abi = json.load(f)["abi"]

contract = w3.eth.contract(
    address="PUT_ADDRESS_HERE",
    abi=abi
)

borrow_counts = {}

events = contract.events.BookBorrowed.get_logs(fromBlock=0)

for e in events:
    book_id = e['args']['id']
    borrow_counts[book_id] = borrow_counts.get(book_id, 0) + 1

print("Most Borrowed Books:")
for book, count in borrow_counts.items():
    print(f"Book {book}: {count} times")
