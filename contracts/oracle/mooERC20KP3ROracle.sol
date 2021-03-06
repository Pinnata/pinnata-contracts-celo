// SPDX-License-Identifier: MIT

pragma solidity 0.6.12;

import './BaseKP3ROracle.sol';
import '../../interfaces/IBaseOracle.sol';
import '../../interfaces/IKeep3rV1Oracle.sol';
import '../../interfaces/IUniswapV2Factory.sol';

contract mooERC20KP3ROracle is IBaseOracle, BaseKP3ROracle {
  constructor(IKeep3rV1Oracle _kp3r) public BaseKP3ROracle(_kp3r) {}

  /// @dev Return the value of the given input as ETH per unit, multiplied by 2**112.
  /// @param token The ERC-20 token to check the value.
  function getCELOPx(address token) external view override returns (uint) {
    if (token == celo) {
      return 2**112;
    }
    address pair = IUniswapV2Factory(factory).getPair(token, mcelo);
    if (token < mcelo) {
      return price0TWAP(pair);
    } else {
      return price1TWAP(pair);
    }
  }
}
