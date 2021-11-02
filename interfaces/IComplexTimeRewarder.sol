// SPDX-License-Identifier: MIT
pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

interface IComplexTimeRewarder {

    struct PoolInfo {
        uint128 accSushiPerShare;
        uint64 lastRewardTime;
        uint64 allocPoint;
    }

    function poolInfo(uint pid) external view returns (uint128 accSushiPerShare, uint64 lastTimeReward, uint64 allocPoint);
    function updatePool(uint256 pid) external;
}