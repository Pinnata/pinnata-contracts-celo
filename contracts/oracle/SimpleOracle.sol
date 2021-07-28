// SPDX-License-Identifier: MIT

pragma solidity 0.6.12;

import '../Governable.sol';
import '../../interfaces/IBaseOracle.sol';

contract SimpleOracle is IBaseOracle, Governable {
  mapping(address => uint) public prices; // Mapping from token to price in CELO (times 2**112).

  /// The governor sets oracle price for a token.
  event SetCELOPx(address token, uint px);

  /// @dev Create the contract and initialize the first governor.
  constructor() public {
    __Governable__init();
  }

  /// @dev Return the value of the given input as CELO per unit, multiplied by 2**112.
  /// @param token The ERC-20 token to check the value.
  function getCELOPx(address token) external view override returns (uint) {
    uint px = prices[token];
    require(px != 0, 'no px');
    return px;
  }

  /// @dev Set the prices of the given token addresses.
  /// @param tokens The token addresses to set the prices.
  /// @param pxs The price data points, representing token value in CELO times 2**112.
  function setCELOPx(address[] memory tokens, uint[] memory pxs) external onlyGov {
    require(tokens.length == pxs.length, 'inconsistent length');
    for (uint idx = 0; idx < tokens.length; idx++) {
      prices[tokens[idx]] = pxs[idx];
      emit SetCELOPx(tokens[idx], pxs[idx]);
    }
  }
}
