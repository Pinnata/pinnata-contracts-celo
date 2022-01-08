// SPDX-License-Identifier: MIT

pragma solidity 0.6.12;

interface ILiquidityGauge {
  function reward_tokens() external view returns (uint[]);

  function minter() external view returns (address);

  function crv_token() external view returns (address);

  function lp_token() external view returns (address);

  function balanceOf(address addr) external view returns (uint);

  function deposit(uint value) external;

  function withdraw(uint value) external;

  function claim_rewards() external;

  function working_balances(address addr) external view returns (uint);
  function working_supply() external view returns (uint);
  
}
