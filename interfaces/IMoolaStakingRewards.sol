// SPDX-License-Identifier: MIT

pragma solidity >=0.4.24;

import './IStakingRewards.sol';

interface IMoolaStakingRewards is IStakingRewards {
    function earnedExternal(address account) external returns (uint256[] calldata);
}