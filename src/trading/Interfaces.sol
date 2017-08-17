pragma solidity ^0.4.13;

import 'ROOT/factories/IterableMapFactory.sol';
import 'ROOT/Controller.sol';

contract Market {
    uint8 private numOutcomes;
    uint256 private maxDisplayPrice;
    uint256 private minDisplayPrice;
    ReportingWindow private reportingWindow;
    uint256 private topic;
    address private shareToken;
    address private denominationToken;

    function getNumberOfOutcomes() public constant returns (uint8) {
        return numOutcomes;
    }

    function getMaxDisplayPrice() public constant returns (uint256) {
        return maxDisplayPrice;
    }

    function getMinDisplayPrice() public constant returns (uint256) {
        return minDisplayPrice;
    }

    function getReportingWindow() public constant returns (ReportingWindow) {
        return reportingWindow;
    }

    function getBranch() public constant returns (Branch) {
        return reportingWindow.getBranch();
    }

    function getTopic() public constant returns (uint256) {
        return topic;
    }

    function getShareToken(uint8) public constant returns (address) {
        return shareToken;
    }

    function getDenominationToken() public constant returns (address) {
        return ;
    }
}


contract ReportingWindow {
    Branch private branch;

    function getBranch() public constant returns (Branch) {
        return branch;
    }
}


contract Branch {
    Topics topics;

    function getTopics() public constant returns (Topics) {
        return topics;
    }
}


contract Topics is Controlled {
    IterableMap topics;
    IterableMapFactory iterableMapFactory;

    function updatePopularity(uint256 _topic, uint256 _fxpAmount) onlyWhitelistedCallers returns (bool) {
        // _oldAmount = topics.getByKeyOrZero(_topic);
        // _newAmount = safeAdd(_oldAmount, _fxpAmount);
        // topics.addOrUpdate(_topic, _newAmount);
        return(true);
    }
}
