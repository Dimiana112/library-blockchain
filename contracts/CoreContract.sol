// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LibraryCore {

    address public admin;
    bool public paused;

    struct Book {
        uint id;
        string title;
        bool available;
    }

    uint public bookCount;
    mapping(uint => Book) public books;
    mapping(address => string) public users;

    event BookAdded(uint id, string title);
    event BookBorrowed(uint id, address user);
    event BookReturned(uint id, address user);

    constructor() {
        admin = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == admin, "Not admin");
        _;
    }

    modifier whenNotPaused() {
        require(!paused, "Paused");
        _;
    }

    function addBook(string memory _title) public onlyOwner {
        bookCount++;
        books[bookCount] = Book(bookCount, _title, true);
        emit BookAdded(bookCount, _title);
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

    function registerUser(string memory name) public {
        users[msg.sender] = name;
    }
}
