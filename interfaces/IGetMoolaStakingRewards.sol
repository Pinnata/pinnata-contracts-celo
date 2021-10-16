// SPDX-License-Identifier: MIT

pragma solidity >=0.4.24;

interface IGetMoolaStakingRewards {
    function externalStakingRewards() external view returns (address);
}