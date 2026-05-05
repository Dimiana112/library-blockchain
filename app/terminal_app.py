import json
from web3 import Web3

# ============================================================
# CONNECT
# ============================================================
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

if not w3.is_connected():
    print("❌ Connection failed")
    exit()

print("✅ Connected to blockchain")

account = w3.eth.accounts[0]

# ============================================================
# LOAD CONTRACTS
# ============================================================
with open("../app_config.json", "r") as f:
    config = json.load(f)

with open("../LibraryCore.json", "r") as f:
    core_data = json.load(f)
    core_abi = core_data["abi"] if "abi" in core_data else core_data

# Hardcoded LibraryCoin ABI (JSON file is broken)
COIN_ABI = [
    {"inputs": [{"name": "", "type": "address"}], "name": "balanceOf",
     "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "to", "type": "address"}, {"name": "amount", "type": "uint256"}],
     "name": "mint", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "to", "type": "address"}, {"name": "amount", "type": "uint256"}],
     "name": "transfer", "outputs": [], "stateMutability": "nonpayable", "type": "function"}
]

core = w3.eth.contract(
    address=Web3.to_checksum_address(config["LibraryCore"]),
    abi=core_abi
)
coin = w3.eth.contract(
    address=Web3.to_checksum_address(config["LibraryCoin"]),
    abi=COIN_ABI
)

# ============================================================
# PERSON 4 — Borrow / Return
# ============================================================
def borrow_book(book_id):
    tx = core.functions.borrowBook(book_id).transact({'from': account})
    w3.eth.wait_for_transaction_receipt(tx)
    print("📖 Book borrowed!")

def return_book(book_id):
    tx = core.functions.returnBook(book_id).transact({'from': account})
    w3.eth.wait_for_transaction_receipt(tx)
    print("📚 Book returned!")
def add_book(title):
    tx = core.functions.addBook(title).transact({'from': account})
    w3.eth.wait_for_transaction_receipt(tx)
    print(f"📕 Added book: {title}")

def list_books():
    count = core.functions.bookCount().call()
    if count == 0:
        print("No books yet.")
        return
    print(f"\n--- Books ({count} total) ---")
    for i in range(1, count + 1):
        book = core.functions.books(i).call()
        status = "✅ available" if book[2] else "❌ borrowed"
        print(f"#{book[0]}  {book[1]}  ({status})")
    print()
# ============================================================
# PERSON 5 — Register / Balance / History
# ============================================================
def register_user(name):
    tx = core.functions.registerUser(name).transact({'from': account})
    w3.eth.wait_for_transaction_receipt(tx)
    print(f"✅ Registered as {name}")

def check_balance():
    eth_balance = w3.from_wei(w3.eth.get_balance(account), "ether")
    try:
        coin_balance = coin.functions.balanceOf(account).call()
    except Exception:
        coin_balance = "N/A (coin contract issue)"
    print(f"\n--- Your Balance ---")
    print(f"Address:      {account}")
    print(f"ETH:          {eth_balance}")
    print(f"LibraryCoin:  {coin_balance}\n")

def view_history():
    print(f"\n--- Activity for {account} ---")
    borrow_filter = core.events.BookBorrowed.create_filter(from_block=0)
    return_filter = core.events.BookReturned.create_filter(from_block=0)

    borrows = [e for e in borrow_filter.get_all_entries() if e['args']['user'] == account]
    returns = [e for e in return_filter.get_all_entries() if e['args']['user'] == account]

    if not borrows and not returns:
        print("No activity yet.\n")
        return

    for e in borrows:
        print(f"📖 Borrowed book #{e['args']['id']}  (block {e['blockNumber']})")
    for e in returns:
        print(f"📚 Returned book #{e['args']['id']}  (block {e['blockNumber']})")
    print()

# ============================================================
# MENU
# ============================================================
print("\n=== Library System ===")
while True:
    print("\n1. Register User")
    print("2. Borrow Book")
    print("3. Return Book")
    print("4. Check My Balance")
    print("5. View My History")
    print("6. List Books")
    print("7. Add Book (admin)")
    print("8. Exit")

    choice = input("Choose: ")

    if choice == "1":
        name = input("Your name: ")
        register_user(name)
    elif choice == "2":
        book_id = int(input("Book ID: "))
        borrow_book(book_id)
    elif choice == "3":
        book_id = int(input("Book ID: "))
        return_book(book_id)
    elif choice == "4":
        check_balance()
    elif choice == "5":
        view_history()
    elif choice == "6":
        list_books()
    elif choice == "7":
        title = input("Book title: ")
        add_book(title)
    elif choice == "8":
        print("Goodbye!")
        break
    else:
        print("Invalid choice")