// SPDX-License-Identifier: MIT

pragma solidity 0.6.12;

import 'OpenZeppelin/openzeppelin-contracts@3.4.0/contracts/token/ERC1155/ERC1155.sol';
import 'OpenZeppelin/openzeppelin-contracts@3.4.0/contracts/token/ERC20/SafeERC20.sol';
import 'OpenZeppelin/openzeppelin-contracts@3.4.0/contracts/utils/ReentrancyGuard.sol';

import '../utils/HomoraMath.sol';
import '../../interfaces/IERC20Wrapper.sol';
import '../../interfaces/IMoolaStakingRewards.sol';
import '../../interfaces/IStakingRewards.sol';

interface IGetMoolaStakingRewards {
    function externalStakingRewards() external view returns (address);
}

interface IGetStakingRewards {
    function rewardsToken() external view returns(address);

    function stakingToken() external view returns(address); 
}

contract WMoolaStakingRewards is ERC1155('WMoolaStakingRewards'), ReentrancyGuard, IERC20Wrapper {
  using SafeMath for uint;
  using HomoraMath for uint;
  using SafeERC20 for IERC20;

  address public immutable staking; // Staking reward contract address
  address public immutable underlying; // Underlying token address
  address public immutable reward; // Reward token address
  mapping(uint256 => uint256[8]) public externalRewards;
  uint public stakingDepth;

  constructor(
    address _staking,
    address _underlying,
    address _reward,
    uint _depth
  ) public {
    staking = _staking;
    underlying = _underlying;
    reward = _reward;
    assert (_depth <= 8);
    stakingDepth = _depth;
    IERC20(_underlying).safeApprove(_staking, uint(-1));
  }

  /// @dev Return the underlying ERC20 for the given ERC1155 token id.
  function getUnderlyingToken(uint) external view override returns (address) {
    return underlying;
  }

  /// @dev Return the conversion rate from ERC1155 to ERC20, multiplied 2**112.
  function getUnderlyingRate(uint) external view override returns (uint) {
    return 2**112;
  }

  /// @dev Mint ERC1155 token for the specified amount
  /// @param amount Token amount to wrap
  function mint(uint amount) external nonReentrant returns (uint) {
    IERC20(underlying).safeTransferFrom(msg.sender, address(this), amount);
    IStakingRewards(staking).stake(amount);
    uint rewardPerToken = IStakingRewards(staking).rewardPerToken();
    address currentStaking = staking;
    for (uint i = 0; i < stakingDepth; i += 1) {
      uint stepReward = IStakingRewards(currentStaking).rewardPerToken();
      externalRewards[rewardPerToken]][i] = stepReward;
      if (i < stakingDepth-1) {
        currentStaking = IGetMoolaStakingRewards(currentStaking).externalStakingRewards();
      }
    }
    _mint(msg.sender, rewardPerToken, amount, '');
    return rewardPerToken;
  }

  /// @dev Burn ERC1155 token to redeem ERC20 token back.
  /// @param id Token id to burn
  /// @param amount Token amount to burn
  function burn(uint id, uint amount) external nonReentrant returns (uint) {
    if (amount == uint(-1)) {
      amount = balanceOf(msg.sender, id);
    }
    _burn(msg.sender, id, amount);
    IStakingRewards(staking).withdraw(amount);
    IStakingRewards(staking).getReward();
    IERC20(underlying).safeTransfer(msg.sender, amount);
    address currentStaking = staking;
    address currentStakingReward = reward;
    for (uint i = 0; i < stakingDepth; i += 1) {
      uint stRewardPerToken = externalRewards[id][i];
      uint enRewardPerToken = IStakingRewards(currentStaking).rewardPerToken();
      uint stReward = stRewardPerToken.mul(amount).divCeil(1e18);
      uint enReward = enRewardPerToken.mul(amount).div(1e18);
      currentStakingReward = IGetStakingRewards(currentStaking).rewardsToken();
      if (enReward > stReward) {
        IERC20(currentStakingReward).safeTransfer(msg.sender, enReward.sub(stReward));
      }
      if (i < stakingDepth-1) {
        currentStaking = IGetMoolaStakingRewards(currentStaking).externalStakingRewards();
      }
    }
    return amount;
  }
}
