pragma solidity 0.4.20;

import 'libraries/token/ERC20.sol';
import 'libraries/Initializable.sol';
import 'reporting/IFeeWindow.sol';


contract IFeeToken is ERC20, Initializable {
    function initialize(IFeeWindow _feeWindow) public returns (bool);
    function getFeeWindow() public view returns (IFeeWindow);
    function feeWindowBurn(address _target, uint256 _amount) public returns (bool);
    function mintForReportingParticipant(address _target, uint256 _amount) public returns (bool);
}