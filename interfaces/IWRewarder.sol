// SPDX-License-Identifier: MIT

pragma solidity 0.6.12;
interface IWRewarder {
  function rewardsPerShare(uint256 pid) external returns (address, uint);
}