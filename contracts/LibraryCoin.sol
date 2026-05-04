// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LibraryCoin {

    //  Admin
    address public admin;

    //  balances
    mapping(address => uint) public balanceOf;

    // total supply
    uint public totalSupply;

    //  constructor
    constructor() {
        admin = msg.sender;
    }

    //  only admin
    modifier onlyAdmin() {
        require(msg.sender == admin, "Not admin");
        _;
    }

    //  mint coins
    function mint(address to, uint amount) public onlyAdmin {
        balanceOf[to] += amount;
        totalSupply += amount;
    }

    // transfer coins
    function transfer(address to, uint amount) public {
        require(balanceOf[msg.sender] >= amount, "Not enough balance");

        balanceOf[msg.sender] -= amount;
        balanceOf[to] += amount;
    }
}
