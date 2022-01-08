// SPDX-License-Identifier: MIT

pragma solidity 0.6.12;

interface ICurvePool {

  function getLpToken() external view returns (address);

  function getBalances() external view returns (uint256[] memory);

  function getToken(uint8 index) public view returns (address);

  function addLiquidity(uint[2] calldata, uint) external;

  function addLiquidity(uint[3] calldata, uint) external;

  function addLiquidity(uint[4] calldata, uint) external;

  function removeLiquidity(uint, uint[2] calldata) external;

  function removeLiquidity(uint, uint[3] calldata) external;

  function removeLiquidity(uint, uint[4] calldata) external;

  function removeLiquidityImbalance(uint[2] calldata, uint) external;

  function removeLiquidityImbalance(uint[3] calldata, uint) external;

  function removeLiquidityImbalance(uint[4] calldata, uint) external;

  function removeLiquidityOneToken(
    uint,
    int128,
    uint
  ) external;

  function getVirtualPrice() external view returns (uint);
}
