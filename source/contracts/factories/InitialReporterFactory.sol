pragma solidity 0.4.20;

import 'libraries/Delegator.sol';
import 'reporting/IInitialReporter.sol';
import 'reporting/IMarket.sol';
import 'IController.sol';


contract InitialReporterFactory {
    function createInitialReporter(IController _controller, IMarket _market, address _designatedReporter) public returns (IInitialReporter) {
        Delegator _delegator = new Delegator(_controller, "InitialReporter");
        IInitialReporter _initialReporter = IInitialReporter(_delegator);
        _initialReporter.initialize(_market, _designatedReporter);
        return _initialReporter;
    }
}
