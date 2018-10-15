pragma solidity 0.4.24;

import 'Controller.sol';

contract TestController is Controller {

    function registerContract(bytes32 _key, address _address) public onlyOwnerCaller returns (bool) {
        registry[_key] = ContractDetails(_key, _address);
        return true;
    }
}
