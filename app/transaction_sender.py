from web3 import Web3

# الاتصال بـ Ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

# تأكدي الاتصال
if w3.is_connected():
    print("Connected to blockchain")
else:
    print("Connection failed")

# حساب المستخدم
account = w3.eth.accounts[0]


# 📚 borrow book
def borrow_book(contract, book_id):
    tx = contract.functions.borrowBook(book_id).transact({'from': account})
    w3.eth.wait_for_transaction_receipt(tx)
    print("Book borrowed!")


# 🔄 return book
def return_book(contract, book_id):
    tx = contract.functions.returnBook(book_id).transact({'from': account})
    w3.eth.wait_for_transaction_receipt(tx)
    print("Book returned!")

def register_user(contract, name):
    tx = contract.functions.registerUser(name).transact({'from': account})
    w3.eth.wait_for_transaction_receipt(tx)
    print("User registered!")
