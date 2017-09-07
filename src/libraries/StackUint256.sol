pragma solidity ^0.4.13;

import "ROOT/libraries/DelegationTarget.sol";
import "ROOT/libraries/Initializable.sol";


contract StackUint256 is DelegationTarget, Ownable {
    
    uint256[] private collection;
    uint256 private head;
    address private owner;
    bool private initialized;

    modifier onlyOwner() {
        require(msg.sender == owner);
        _;
    }

    function initialize(address _owner) external beforeInitialized returns (bool) {
        endInitialization();
        initialized = true;
        owner = _owner;
        return (true);
    }

    function push(uint256 _item) public onlyOwner returns (bool) {
        head += 1;
        collection.push(_item);
        return (true);
    }    

    function pop() public onlyOwner returns (uint256) {
        uint256 _index = head;
        require(_index != 0);
        head = _index - 1;
        uint256 _removedValue = collection[_index];
        delete collection[_index];
        return (_removedValue);
    }

    function peek() public constant returns (uint256) {
        require(head != 0);
        return (collection[head]);
    }

    function isEmpty() public constant returns (bool) {
        return (head == 0);
    }
}

