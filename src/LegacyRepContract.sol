pragma solidity ^0.4.13;

import 'ROOT/libraries/token/VariableSupplyToken.sol';
import 'ROOT/libraries/token/ERC20.sol';


contract LegacyRepContract is VariableSupplyToken {
    event FundedAccount(address indexed _branch, address indexed _sender, uint256 _repBalance, uint256 _timestamp);

    uint256 private constant DEFAULT_FAUCET_AMOUNT = 47 ether;

    string public constant name = "Reputation";
    string public constant symbol = "REP";
    uint256 public constant decimals = 18;

    function LegacyRepContract() {
        // This is to confirm we are on test net
        address _foundationRepAddress = address(0xe94327d07fc17907b4db788e5adf2ed424addff6);
        uint256 size;
        assembly { size := extcodesize(_foundationRepAddress) }
        require(size == 0);
    }

    function faucet(uint256 _amount) public returns (bool) {
        if (_amount == 0) {
            _amount = DEFAULT_FAUCET_AMOUNT;
        }
        require(_amount < 2 ** 128);
        mint(msg.sender, _amount);
        FundedAccount(this, msg.sender, _amount, block.timestamp);
        return true;
    }
}
