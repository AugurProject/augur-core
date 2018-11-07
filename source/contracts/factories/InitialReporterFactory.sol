pragma solidity 0.4.24;

import 'libraries/CloneFactory.sol';
import 'reporting/IInitialReporter.sol';
import 'reporting/IMarket.sol';
import 'IController.sol';
import 'IControlled.sol';


contract InitialReporterFactory is CloneFactory {
    function createInitialReporter(IController _controller, IMarket _market, address _designatedReporter) public returns (IInitialReporter) {
        IInitialReporter _initialReporter = IInitialReporter(createClone(_controller.lookup("InitialReporter")));
        IControlled(_initialReporter).setController(_controller);
        _initialReporter.initialize(_market, _designatedReporter);
        return _initialReporter;
    }
}
