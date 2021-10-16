// SPDX-License-Identifier: MIT

pragma solidity >=0.4.24;

// https://docs.synthetix.io/contracts/source/interfaces/istakingrewards
interface IGetStakingRewards {
    function rewardsToken() external view returns(address);

    function stakingToken() external view returns(address); 
}