// SPDX-License-Identifier: MIT

pragma solidity 0.6.12;

import '../../interfaces/IBaseOracle.sol';

interface IGetMoolaUnderlying {
    function underlyingAssetAddress() external view returns (address);
}

contract MoolaProxyOracle is IBaseOracle {
  IBaseOracle public immutable source; // Main oracle source

  constructor(IBaseOracle _source) public {
    source = _source;
  }

  /// @dev Return the value of the given input as CELO per unit, multiplied by 2**112.
  /// @param token The ERC-20 token to check the value.
  function getCELOPx(address token) external view override returns (uint) {
    address underlying = IGetMoolaUnderlying(token).underlyingAssetAddress();
    uint px = IBaseOracle(source).getCELOPx(underlying);
    require(px != 0, 'no px');
    return px;
  }

}