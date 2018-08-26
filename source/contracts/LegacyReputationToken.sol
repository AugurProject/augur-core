pragma solidity 0.4.24;

import 'libraries/ContractExists.sol';
import 'legacy_reputation/OldLegacyRepToken.sol';


contract LegacyReputationToken is OldLegacyReputationToken {
    using ContractExists for address;
    event FundedAccount(address indexed _universe, address indexed _sender, uint256 _repBalance, uint256 _timestamp);

    address private constant FOUNDATION_REP_ADDRESS = address(0x1985365e9f78359a9B6AD760e32412f4a445E862);

    string public constant name = "Reputation";
    string public constant symbol = "REP";
    uint256 public constant decimals = 18;

    constructor() public {
        // This is to confirm we are not on foundation network
        require(!FOUNDATION_REP_ADDRESS.exists());
    }

    function faucet(uint256 _amount) public returns (bool) {
        require(_amount < 2 ** 128);
        mint(msg.sender, _amount);
        emit FundedAccount(this, msg.sender, _amount, block.timestamp);
        return true;
    }

    function onMint(address, uint256) internal returns (bool) {
        return true;
    }

    function onBurn(address, uint256) internal returns (bool) {
        return true;
    }

    function onTokenTransfer(address, address, uint256) internal returns (bool) {
        return true;
    }
}
