pragma solidity ^0.4.13;

import 'ROOT/legacy_reputation/StandardToken.sol';
import 'ROOT/legacy_reputation/Ownable.sol';
import 'ROOT/Controller.sol';


contract LegacyRepContract is StandardToken, Controlled, Ownable {
    using SafeMath for uint256;

    event FundedAccount(address indexed _branch, address indexed _sender, uint256 _repBalance, uint256 _timestamp);

    uint256 private constant FAUCET_AMOUNT = 47 ether;

    string public constant name = "Reputation";
    string public constant symbol = "REP";
    uint256 public constant decimals = 18;

    uint256 private creation;
    bool private seeded;

    modifier doneCreating() {
        require(!isCreating());
        _;
    }

    modifier stillCreating() {
        require(isCreating());
        _;
    }

    function LegacyRepContract() {
        owner = msg.sender;
        creation = block.timestamp;
    }

    function isCreating() private returns (bool) {
        return !seeded || block.timestamp < (creation + 15000);
    }

    function faucet() public doneCreating returns (bool) {
        require(balanceOf(msg.sender) == 0);
        balances[this] = balances[this].sub(FAUCET_AMOUNT);
        balances[msg.sender] = FAUCET_AMOUNT;
        FundedAccount(this, msg.sender, FAUCET_AMOUNT, block.timestamp);
        return true;
    }

    function transfer(address _to, uint256 _value) public doneCreating returns (bool) {
        balances[msg.sender] = balances[msg.sender].sub(_value);
        balances[_to] = balances[_to].add(_value);
        Transfer(msg.sender, _to, _value);
        return true;
    }

    function setSaleDistribution(address[] _addresses, uint256[] _balances) public onlyOwner stillCreating returns (bool) {
        require(_addresses.length == _balances.length);
        for (uint8 i = 0; i < _addresses.length; i++) {
            if (balanceOf(_addresses[i]) == 0 && !seeded) {
                balances[_addresses[i]] = _balances[i];
                totalSupply += _balances[i];
                Transfer(0, _addresses[i], _balances[i]);
            }
        }
        if (totalSupply == 11000000 ether) {
            seeded = true;
        }
        require(totalSupply <= 11000000 ether);
        return true;
    }

    function getRidOfDustForLaunch() public onlyOwner returns (bool) {
        require (balances[0] != 0);
        totalSupply -= balances[0];
        balances[0] = 0;
        return true;
    }

    function getSeeded() public constant returns (bool) {
        return seeded;
    }
}