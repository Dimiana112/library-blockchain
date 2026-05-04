// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LibraryCore {

  
    //  Admin
    address public admin;

    //  Pause System
    
    bool public paused;

  
    //  Book Structure
   
    struct Book {
        uint id;
        string title;
        bool available;
    }

    uint public bookCount;
    mapping(uint => Book) public books;

    //  Users
  
    mapping(address => string) public users;

    // Events
 
    event BookAdded(uint id, string title);
    event BookBorrowed(uint id, address user);
    event BookReturned(uint id, address user);

   // Constructor
    
    constructor() {
        admin = msg.sender;
    }

   // Modifiers
    
    modifier onlyOwner() {
        require(msg.sender == admin, "Not admin");
        _;
    }

    modifier whenNotPaused() {
        require(!paused, "System is paused");
        _;
    }

  // Book Functions
   

    function addBook(string memory _title) public onlyOwner {
        bookCount++;
        books[bookCount] = Book(bookCount, _title, true);

        emit BookAdded(bookCount, _title);
    }

    // Batch Add Books (NEW)
    function addBooksBatch(string[] memory titles) public onlyOwner {
        for (uint i = 0; i < titles.length; i++) {
            bookCount++;
            books[bookCount] = Book(bookCount, titles[i], true);

            emit BookAdded(bookCount, titles[i]);
        }
    }

    function borrowBook(uint _id) public whenNotPaused {
        require(books[_id].available, "Not available");

        books[_id].available = false;

        emit BookBorrowed(_id, msg.sender);
    }

    function returnBook(uint _id) public whenNotPaused {
        books[_id].available = true;

        emit BookReturned(_id, msg.sender);
    }

    // User Functions
    

    function registerUser(string memory name) public {
        require(bytes(users[msg.sender]).length == 0, "Already registered");
        users[msg.sender] = name;
    }

   // Admin Control
    

    function getAdmin() public view returns(address) {
        return admin;
    }

    function pause() public onlyOwner {
        paused = true;
    }

    function resume() public onlyOwner {
        paused = false;
    }

    function transferOwnership(address newAdmin) public onlyOwner {
        require(newAdmin != address(0), "Invalid address");
        admin = newAdmin;
    }
}
