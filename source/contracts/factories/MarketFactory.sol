pragma solidity 0.4.20;


import 'libraries/Delegator.sol';
import 'reporting/IMarket.sol';
import 'reporting/IReputationToken.sol';
import 'trading/ICash.sol';
import 'IController.sol';


contract MarketFactory {
    function createMarket(IController _controller, IUniverse _universe, uint256 _endTime, uint256 _feePerEthInWei, ICash _denominationToken, address _designatedReporterAddress, address _sender, uint256 _numOutcomes, uint256 _numTicks) public payable returns (IMarket _market) {
        Delegator _delegator = new Delegator(_controller, "Market");
        _market = IMarket(_delegator);
        IReputationToken _reputationToken = _universe.getReputationToken();
        require(_reputationToken.transfer(_market, _reputationToken.balanceOf(this)));
        _market.initialize.value(msg.value)(_universe, _endTime, _feePerEthInWei, _denominationToken, _designatedReporterAddress, _sender, _numOutcomes, _numTicks);
        return _market;
    }
}
