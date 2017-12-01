pragma solidity 0.4.18;

import 'ITime.sol';
import 'libraries/ContractExists.sol';
import 'libraries/Ownable.sol';


contract TimeControlled is ITime, Ownable {
    using ContractExists for address;

    uint256 private timestamp = 1;
    address private constant FOUNDATION_REP_ADDRESS = address(0xE94327D07Fc17907b4DB788E5aDf2ed424adDff6);

    function TimeControlled() public {
        // This is to confirm we are not on foundation network
        require(!FOUNDATION_REP_ADDRESS.exists());
        timestamp = block.timestamp;
    }

    function getTimestamp() external view returns (uint256) {
        return timestamp;
    }

    function incrementTimestamp(uint256 _amount) external onlyOwner returns (bool) {
        timestamp += _amount;
        return true;
    }

    function setTimestamp(uint256 _timestamp) external onlyOwner returns (bool) {
        timestamp = _timestamp;
        return true;
    }

    function getTypeName() public view returns (bytes32) {
        return "TimeControlled";
    }
}
