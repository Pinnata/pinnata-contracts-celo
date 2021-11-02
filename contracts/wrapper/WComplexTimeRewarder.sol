pragma solidity 0.6.12;

import 'OpenZeppelin/openzeppelin-contracts@3.4.0/contracts/token/ERC20/SafeERC20.sol';

import '../../interfaces/IComplexTimeRewarder.sol';
import '../../interfaces/IWRewarder.sol';

contract WComplexTimeRewarder is IWRewarder {
  using SafeMath for uint;
  using SafeERC20 for IERC20;

  address public immutable rewarder;
  address public immutable rewardToken;

  constructor(address _rewarder, address _rewardToken) public {
    rewarder = _rewarder;
    rewardToken = _rewardToken;
  }

  function rewardsPerShare(uint pid) override external returns (address, uint) {
    IComplexTimeRewarder(rewarder).updatePool(pid);
    (uint128 _rewardAmount, , ) = IComplexTimeRewarder(rewarder).poolInfo(pid);
    return (rewardToken, uint(_rewardAmount));
  }
}