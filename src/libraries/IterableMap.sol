pragma solidity ^0.4.13;

import 'ROOT/Controller.sol';

contract IterableMap {

    struct Item {
        uint hasItem;
        var value;
        var offset;
    }

    address owner;
    uint initialied;
    var[] itemsArray;
    Item[] itemsMap;
    uint numberOfItems;

    function any() {
         if (this.initialized) {
             require(msg.sender == this.owner || msg.sender == this);
         }
    }

    function initialize(address owner) returns (uint) {
         require(!this.initialized);
         this.initialized = true;
         this.owner = owner;
         return (uint(1));
    }

    function add(var key, var value) returns (uint) {
         require(!this.contains(key));
         this.itemsArray[this.numberOfItems] = key;
	     this.itemsMap[key].hasValue = true;
         this.itemsMap[key].value = value;
         this.itemsMap[key].offset = this.numberOfItems;
         this.numberOfItems += 1;
         return (uint(1));
    }

    function update(var key, var value) returns (uint) {
         require(this.contains(key));
         this.itemsMap[key].value = value;
         return (uint(1));
    }

    function addOrUpdate(var key, var value) returns (uint) {
        if (!this.contains(key)) {
            this.add(key, value);
        } 
        
        else {
            this.update(key, value);
        }

        return (uint(1));
    }

    function remove(var key) returns (uint) {
	    require(this.contains(key));
        var keyRemovedOffset = this.itemsMap[key].offset;
        this.itemsArray[keyRemovedOffset] = 0;
        this.itemsMap[key].hasValue = false;
        this.itemsMap[key].value = 0;
        this.itemsMap[key].offset = 0;
        
        if (this.numberOfItems > 1 && keyRemovedOffset != (this.numberOfItems - 1)) {
        /* move tail item in collection to the newly opened slot from the key we just removed if not last or only item being removed */
            var tailItemKey = this.getByOffset(this.numberOfItems - 1);
            this.itemsArray[this.numberOfItems - 1] = 0;
            this.itemsArray[keyRemovedOffset] = tailItemKey;
            this.itemsMap[tailItemKey].offset = this.numberOfItems - 2;
        }
   
        this.numberOfItems -= 1;
        return (uint(1));
    }

    function getByKeyOrZero(var key) returns (var) {
        return this.itemsMap[key].value;
    }

    function getByKey(var key) returns (var) {
        require(this.itemsMap[key].hasValue);
        return (this.itemsMap[key].value);
    }
   
    function getByOffset(var offset) returns (var) {
        require(0 <= offset && offset < this.numberOfItems);
        return this.itemsArray[offset];
    }

    function contains(var key) returns (uint) {
        if (this.itemsMap[key].hasValue) {
            return (uint(1));
	}
        return (uint(0));
    }

    function count() returns (uint) {
        return this.numberOfItems;
    }
}
