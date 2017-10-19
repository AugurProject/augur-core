pragma solidity ^0.4.17;

import 'libraries/ContractExists.sol';


contract ContractExistsHelper {
    using ContractExists for address;

    function doesContractExist(address _address) public view returns (bool) {
        return _address.exists();
    }
}
