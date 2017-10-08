pragma solidity 0.4.17;
pragma experimental ABIEncoderV2;
pragma experimental "v0.5.0";

import 'IController.sol';
import 'libraries/token/ERC20Basic.sol';


contract IControlled {
    function setController(IController _controller) public returns(bool);
    function suicideFunds(address _target, ERC20Basic[] _tokens) public returns(bool);
}
