pragma solidity 0.4.24;


import 'libraries/CloneFactory.sol';
import 'reporting/IMarket.sol';
import 'reporting/IReputationToken.sol';
import 'trading/ICash.sol';
import 'IController.sol';
import 'IControlled.sol';


contract MarketFactory is CloneFactory {
    function createMarket(IController _controller, IUniverse _universe, uint256 _endTime, uint256 _feePerEthInWei, address _designatedReporterAddress, address _sender, uint256 _numOutcomes, uint256 _numTicks) public payable returns (IMarket _market) {
        _market = IMarket(createClone(_controller.lookup("Market")));
        IControlled(_market).setController(_controller);
        IReputationToken _reputationToken = _universe.getReputationToken();
        require(_reputationToken.transfer(_market, _reputationToken.balanceOf(this)));
        _market.initialize.value(msg.value)(_universe, _endTime, _feePerEthInWei, _designatedReporterAddress, _sender, _numOutcomes, _numTicks);
        return _market;
    }
}
