// SPDX-License-Identifier: MIT
pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

interface IMiniChefV2 {
    function SUSHI() external view returns (address);


    struct UserInfo {
        uint256 amount;
        uint256 rewardDebt;
    }

    struct PoolInfo {
        uint128 accSushiPerShare;
        uint64 lastRewardTime;
        uint64 allocPoint;
    }

    function poolInfo(uint pid) external view returns (uint128 accSushiPerShare, uint64 lastTimeReward, uint64 allocPoint);
    function sushiPerSecond() external view returns (uint);
    function totalAllocPoint() external view returns (uint);
    function lpToken(uint pid) external view returns (address);
    function poolLength() external view returns (uint256);
    function updatePool(uint256 pid) external;
    function userInfo(uint256 _pid, address _user) external view returns (uint256, uint256);
    function deposit(uint256 pid, uint256 amount, address to) external;
    function withdraw(uint256 pid, uint256 amount, address to) external;
    function harvest(uint256 pid, address to) external;
    function withdrawAndHarvest(uint256 pid, uint256 amount, address to) external;
    function emergencyWithdraw(uint256 pid, address to) external;
}