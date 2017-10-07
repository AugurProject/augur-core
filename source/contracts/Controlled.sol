pragma solidity ^0.4.17;

import 'IControlled.sol';
import 'IController.sol';
import 'libraries/token/ERC20Basic.sol';


contract Controlled is IControlled {
    IController internal controller;

    modifier onlyWhitelistedCallers {
        require(controller.assertIsWhitelisted(msg.sender));
        _;
    }

    modifier onlyControllerCaller {
        require(IController(msg.sender) == controller);
        _;
    }

    modifier onlyInGoodTimes {
        require(controller.stopInEmergency());
        _;
    }

    modifier onlyInBadTimes {
        require(controller.onlyInEmergency());
        _;
    }

    function Controlled() {
        controller = IController(msg.sender);
    }

    function getController() public constant returns(IController) {
        return controller;
    }

    function setController(IController _controller) public onlyControllerCaller returns(bool) {
        controller = _controller;
        return true;
    }

    function suicideFunds(address _target, ERC20Basic[] _tokens) public onlyControllerCaller returns(bool) {
        // Transfer tokens to target
        for (uint256 i = 0; i < _tokens.length; i++) {
            ERC20Basic token = _tokens[i];
            uint256 balance = token.balanceOf(this);
            token.transfer(_target, balance);
        }

        // Transfer Eth to target and terminate contract
        selfdestruct(_target);
        return true;
    }
}
