pragma solidity 0.4.20;


// Utility to check if the address actually contains a contract based on size.
library ContractExists {
    function exists(address _address) internal view returns (bool) {
        uint256 size;
        assembly { size := extcodesize(_address) }
        return size > 0;
    }
}
