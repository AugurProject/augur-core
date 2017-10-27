pragma solidity 0.4.17;


import 'IControlled.sol';
import 'IController.sol';
import 'libraries/token/ERC20Basic.sol';


contract Controlled is IControlled {
    IController internal controller;
    // Inidcates whether ETH may be extracted from this contract by the controller. It should only be allowed when ETH cannot legitimately be held by the contract
    bool internal mayExtractETH = true;
    mapping(address => bool) tokenExtractionDisallowed;

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

    function Controlled() public {
        controller = IController(msg.sender);
    }

    function getController() public view returns(IController) {
        return controller;
    }

    function setController(IController _controller) public onlyControllerCaller returns(bool) {
        controller = _controller;
        return true;
    }

    function suicideFunds(address _target, ERC20Basic[] _tokens) public onlyControllerCaller returns(bool) {
        // Transfer tokens to target
        for (uint256 i = 0; i < _tokens.length; i++) {
            ERC20Basic _token = _tokens[i];
            uint256 _balance = _token.balanceOf(this);
            _token.transfer(_target, _balance);
        }

        // Transfer Eth to target and terminate contract
        selfdestruct(_target);
        return true;
    }

    // Send accidentally received ETH to the controller
    function extractETH() public onlyControllerCaller returns(bool) {
        require(mayExtractETH);
        require(controller.call.value(this.balance)());
        return true;
    }

    // Send accidentally received tokens to the controller
    function extractTokens(ERC20Basic _token) public onlyControllerCaller returns (bool) {
        require(!tokenExtractionDisallowed[_token]);
        uint256 _balance = _token.balanceOf(this);
        _token.transfer(controller, _balance);
        return true;
    }
}
