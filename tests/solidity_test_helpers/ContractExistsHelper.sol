pragma solidity ^0.4.20;

import 'libraries/ContractExists.sol';


contract ContractExistsHelper {
    using ContractExists for address;

    function doesContractExist(address _address) public view returns (bool) {
        return _address.exists();
    }
}
