from web3 import Web3
import json

from transaction_sender import borrow_book
from transaction_sender import return_book
from transaction_sender import register_user

# 🔗 connect to blockchain
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

# 📄 load contract ABI
with open("LibraryCore.json") as f:
    contract_data = json.load(f)

abi = contract_data["abi"]

# ⚠️ حطي العنوان هنا بعد deploy
contract = w3.eth.contract(
    address="PUT_ADDRESS_HERE",
    abi=abi
)

print("=== Library System ===")

while True:
    print("\n1. Register User")
    print("2. Borrow Book")
    print("3. Return Book")
    print("4. Exit")

    choice = input("Choose an option: ")

    if choice == "1":
        name = input("Enter your name: ")
        register_user(contract, name)

    elif choice == "2":
        try:
            book_id = int(input("Enter Book ID: "))
            borrow_book(contract, book_id)
        except:
            print("Invalid input")

    elif choice == "3":
        try:
            book_id = int(input("Enter Book ID: "))
            return_book(contract, book_id)
        except:
            print("Invalid input")

    elif choice == "4":
        print("Goodbye!")
        break

    else:
        print("Invalid choice")
