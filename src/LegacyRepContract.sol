pragma solidity ^0.4.13;

import 'ROOT/libraries/token/VariableSupplyToken.sol';
import 'ROOT/libraries/token/ERC20.sol';


contract LegacyRepContract is VariableSupplyToken {
    event FundedAccount(address indexed _branch, address indexed _sender, uint256 _repBalance, uint256 _timestamp);

    uint256 private constant FAUCET_AMOUNT = 47 ether;

    string public constant name = "Reputation";
    string public constant symbol = "REP";
    uint256 public constant decimals = 18;

    address private creator;

    function LegacyRepContract() {
        // This is to confirm we are on test net
        address _foundationRepAddress = address(0xe94327d07fc17907b4db788e5adf2ed424addff6);
        uint256 size;
        assembly { size := extcodesize(_foundationRepAddress) }
        require(size == 0);
        // Store the creator for use in automated testing funding
        creator = msg.sender;
    }

    function faucet() public returns (bool) {
        require(balanceOf(msg.sender) == 0);
        mint(msg.sender, FAUCET_AMOUNT);
        FundedAccount(this, msg.sender, FAUCET_AMOUNT, block.timestamp);
        return true;
    }

    // Function for automated testing
    function testFund(uint256 _amount) public returns (bool) {
        require(msg.sender == creator);
        mint(msg.sender, _amount);
    }
}