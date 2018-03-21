pragma solidity 0.4.20;

import 'Controller.sol';

contract TestController is Controller {

    function registerContract(bytes32 _key, address _address, bytes20 _commitHash, bytes32 _bytecodeHash) public onlyOwnerCaller returns (bool) {
        registry[_key] = ContractDetails(_key, _address, _commitHash, _bytecodeHash);
        return true;
    }
}