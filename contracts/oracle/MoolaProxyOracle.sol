// SPDX-License-Identifier: MIT

pragma solidity 0.6.12;

import '../../interfaces/IBaseOracle.sol';

contract MoolaProxyOracle is IBaseOracle {
  IBaseOracle public immutable source; // Main oracle source
  mapping(address => address) public moolaToUnderlying;

  constructor(IBaseOracle _source) public {
    source = _source;
    moolaToUnderlying[0x918146359264C492BD6934071c6Bd31C854EDBc3] = 0x765DE816845861e75A25fCA122bb6898B8B1282a;
    moolaToUnderlying[0xE273Ad7ee11dCfAA87383aD5977EE1504aC07568] = 0xD8763CBa276a3738E6DE85b4b3bF5FDed6D6cA73;
  }

  /// @dev Return the value of the given input as CELO per unit, multiplied by 2**112.
  /// @param token The ERC-20 token to check the value.
  function getCELOPx(address token) external view override returns (uint) {
    address underlying = moolaToUnderlying[token];
    uint px = IBaseOracle(source).getCELOPx(underlying);
    require(px != 0, 'no px');
    return px;
  }

}