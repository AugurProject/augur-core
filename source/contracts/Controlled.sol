pragma solidity 0.4.24;


import 'IControlled.sol';
import 'IController.sol';
import 'libraries/token/ERC20Basic.sol';


contract Controlled is IControlled {
    IController internal controller;

    modifier onlyWhitelistedCallers {
        require(controller.assertIsWhitelisted(msg.sender));
        _;
    }

    modifier onlyCaller(bytes32 _key) {
        require(msg.sender == controller.lookup(_key));
        _;
    }

    modifier onlyControllerCaller {
        require(IController(msg.sender) == controller || controller == address(0));
        _;
    }

    modifier onlyKeyHolder {
        require(msg.sender == controller.owner());
        _;
    }

    constructor() public {
        controller = IController(msg.sender);
    }

    function getController() public view returns(IController) {
        return controller;
    }

    function setController(IController _controller) public onlyControllerCaller returns(bool) {
        controller = _controller;
        return true;
    }
}
