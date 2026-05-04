from transaction_sender import borrow_book
from transaction_sender import return_book
contract = None
print("=== Library System ===")

while True:
    print("\n1. Register User")
    print("2. Borrow Book")
    print("3. Return Book")
    print("4. Exit")

    choice = input("Choose an option: ")

    if choice == "1":
        name = input("Enter your name: ")
        print(f"User {name} registered")

    elif choice == "2":
        book_id = int(input("Enter Book ID: "))
        borrow_book(contract, book_id)

    elif choice == "3":
        book_id = int(input("Enter Book ID: "))
        return_book(contract, book_id)

    elif choice == "4":
        print("Goodbye!")
        break

    else:
        print("Invalid choice")
