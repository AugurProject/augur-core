pragma solidity 0.4.17;
pragma experimental ABIEncoderV2;
pragma experimental "v0.5.0";

import 'reporting/IReportingEscapeHatch.sol';
import 'libraries/DelegationTarget.sol';


contract ReportingEscapeHatch is DelegationTarget, IReportingEscapeHatch {
    // TODO: figure out how the reporting system escape hatch works and implement it
}
