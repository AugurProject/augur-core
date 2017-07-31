pragma solidity ^0.4.13;

import 'ROOT/Controller.sol';

contract Stack {
    
    var[] collection;
    uint head;
    address owner;
    bool initialized;

    function any() {
         if (initialized) {
             require(msg.sender == this.owner || msg.sender == this);
         }
    }

    function initialize(address owner) returns (uint) {
         require(!this.initialized);
         this.initialized = true;
         this.owner = owner;
         return (uint(1));
    }

    function push(var item) returns (uint) {
         uint index = this.head + 1;
         this.head = index;
         this.collection[index] = item;
         return (uint(1));
    }    

    function pop() returns (var) {
         uint index = this.head;
         require(index != 0);
         this.head = index - 1;
         var removedValue = this.collection[index];
         this.collection[index] = 0;
         return (removedValue);
    }

    function peek() returns (var) {
         uint index = this.head;
         require(index != 0);
         return (this.collection[index]);
    }

    function isEmpty() returns (bool) {
         return (this.head == 0);
    }
}
