pragma solidity 0.6.12;

import 'OpenZeppelin/openzeppelin-contracts@3.4.0/contracts/token/ERC1155/ERC1155.sol';
import 'OpenZeppelin/openzeppelin-contracts@3.4.0/contracts/token/ERC20/SafeERC20.sol';
import 'OpenZeppelin/openzeppelin-contracts@3.4.0/contracts/utils/ReentrancyGuard.sol';

import '../utils/HomoraMath.sol';
import '../Governable.sol';
import '../../interfaces/IERC20Wrapper.sol';
import '../../interfaces/IMiniChefV2.sol';
import '../../interfaces/IWRewarder.sol';

contract WMiniChefV2 is ERC1155('WMiniChefV2'), ReentrancyGuard, IERC20Wrapper, Governable {
  using SafeMath for uint;
  using HomoraMath for uint;
  using SafeERC20 for IERC20;

  IMiniChefV2 public immutable chef; // Sushiswap miniChef
  IERC20 public immutable sushi; // Sushi token
  mapping (uint => address) public wrewarder; // pid to wrapped rewarder
  mapping (uint => mapping (address => uint)) public externalRewards; // id to external rewards;
  uint private storedSushiPerShare; 

  constructor(IMiniChefV2 _chef) public {
    chef = _chef;
    sushi = IERC20(_chef.SUSHI());
    __Governable__init();
  }

  function set(uint _pid, IWRewarder _wrewarder) external onlyGov {
    wrewarder[_pid] = address(_wrewarder);
  }

  /// @dev Encode pid, sushiPerShare to ERC1155 token id
  /// @param pid Pool id (16-bit)
  /// @param sushiPerShare Sushi amount per share, multiplied by 1e18 (240-bit)
  function encodeId(uint pid, uint sushiPerShare) public pure returns (uint id) {
    require(pid < (1 << 16), 'bad pid');
    require(sushiPerShare < (1 << 240), 'bad sushi per share');
    return (pid << 240) | sushiPerShare;
  }

  /// @dev Decode ERC1155 token id to pid, sushiPerShare
  /// @param id Token id
  function decodeId(uint id) public pure returns (uint pid, uint sushiPerShare) {
    pid = id >> 240; // First 16 bits
    sushiPerShare = id & ((1 << 240) - 1); // Last 240 bits
  }

  /// @dev Return the underlying ERC-20 for the given ERC-1155 token id.
  /// @param id Token id
  function getUnderlyingToken(uint id) external view override returns (address) {
    (uint pid, ) = decodeId(id);
    return chef.lpToken(pid);
  }

  /// @dev Return the conversion rate from ERC-1155 to ERC-20, multiplied by 2**112.
  function getUnderlyingRate(uint) external view override returns (uint) {
    return 2**112;
  }

  /// @dev Mint ERC1155 token for the given pool id.
  /// @param pid Pool id
  /// @param amount Token amount to wrap
  /// @return The token id that got minted.
  function mint(uint pid, uint amount) external nonReentrant returns (uint) {
    chef.updatePool(pid);
    address lpToken = chef.lpToken(pid);
    IERC20(lpToken).safeTransferFrom(msg.sender, address(this), amount);
    if (IERC20(lpToken).allowance(address(this), address(chef)) != uint(-1)) {
      // We only need to do this once per pool, as LP token's allowance won't decrease if it's -1.
      IERC20(lpToken).safeApprove(address(chef), uint(-1));
    }
    chef.deposit(pid, amount, address(this));
    (uint sushiPerShare, ,) = chef.poolInfo(pid);
    uint id = encodeId(pid, sushiPerShare);
    _mint(msg.sender, id, amount, '');
    // Exteral rewards
    address wrewards = wrewarder[pid]; 
    if (wrewards != address(0)) {
      (address rewardToken, uint256 rewardAmount) = IWRewarder(wrewards).rewardsPerShare(pid);
      if (rewardToken != address(0)) {
        externalRewards[id][rewardToken] = rewardAmount;
      }
    }
    return id;
  }

  /// @dev Burn ERC1155 token to redeem LP ERC20 token back plus SUSHI rewards.
  /// @param id Token id
  /// @param amount Token amount to burn
  /// @return The pool id that that you will receive LP token back.
  function burn(uint id, uint amount) external nonReentrant returns (uint) {
    if (amount == uint(-1)) {
      amount = balanceOf(msg.sender, id);
    }
    (uint pid, uint stSushiPerShare) = decodeId(id);
    _burn(msg.sender, id, amount);
    chef.updatePool(pid);
    (uint enSushiPerShare, , ) = chef.poolInfo(pid);
    if (enSushiPerShare > storedSushiPerShare) {
      chef.withdrawAndHarvest(pid, amount, address(this));
    } else {
      chef.withdraw(pid, amount, address(this));
    }
    storedSushiPerShare = enSushiPerShare;
    {
    address lpToken = chef.lpToken(pid);
    IERC20(lpToken).safeTransfer(msg.sender, amount);
    uint stSushi = stSushiPerShare.mul(amount).divCeil(1e12);
    uint enSushi = enSushiPerShare.mul(amount).div(1e12);
    if (enSushi > stSushi) {
      uint bal = sushi.balanceOf(address(this));
      if (enSushi.sub(stSushi) < bal) {
        sushi.safeTransfer(msg.sender, enSushi.sub(stSushi));
      } else {
        sushi.safeTransfer(msg.sender, bal);
      }
    }
    }
    // External rewards
    address wrewards = wrewarder[pid]; 
    if (wrewards != address(0)) {
      (address rewardToken, uint enRewardPerShare) = IWRewarder(wrewards).rewardsPerShare(pid);
      uint stRewardPerShare = externalRewards[id][rewardToken];
      uint stReward = stRewardPerShare.mul(amount).divCeil(1e12);
      uint enReward = enRewardPerShare.mul(amount).div(1e12);
      if (enReward > stReward) {
        uint bal = IERC20(rewardToken).balanceOf(address(this));
        if (enReward.sub(stReward) < bal) {
          IERC20(rewardToken).safeTransfer(msg.sender, enReward.sub(stReward));
        } else {
          IERC20(rewardToken).safeTransfer(msg.sender, bal);
        }
      }
    }
    return pid;
  }

/// @dev Withdraw from Sushi without caring about rewards
function emergencyBurn(uint id, uint amount) external nonReentrant returns (uint) {
    if (amount == uint(-1)) {
      amount = balanceOf(msg.sender, id);
    }
    (uint pid, uint stSushiPerShare) = decodeId(id);
    _burn(msg.sender, id, amount);
    chef.updatePool(pid);
    (uint enSushiPerShare, , ) = chef.poolInfo(pid);
    chef.emergencyWithdraw(pid, address(this));
    storedSushiPerShare = enSushiPerShare;
    {
    address lpToken = chef.lpToken(pid);
    IERC20(lpToken).safeTransfer(msg.sender, amount);
    uint stSushi = stSushiPerShare.mul(amount).divCeil(1e12);
    uint enSushi = enSushiPerShare.mul(amount).div(1e12);
    if (enSushi > stSushi) {
      uint bal = sushi.balanceOf(address(this));
      if (enSushi.sub(stSushi) < bal) {
        sushi.safeTransfer(msg.sender, enSushi.sub(stSushi));
      } else {
        sushi.safeTransfer(msg.sender, bal);
      }
    }
    }
    // External rewards
    address wrewards = wrewarder[pid]; 
    if (wrewards != address(0)) {
      (address rewardToken, uint enRewardPerShare) = IWRewarder(wrewards).rewardsPerShare(pid);
      uint stRewardPerShare = externalRewards[id][rewardToken];
      uint stReward = stRewardPerShare.mul(amount).divCeil(1e12);
      uint enReward = enRewardPerShare.mul(amount).div(1e12);
      if (enReward > stReward) {
        uint bal = IERC20(rewardToken).balanceOf(address(this));
        if (enReward.sub(stReward) < bal) {
          IERC20(rewardToken).safeTransfer(msg.sender, enReward.sub(stReward));
        } else {
          IERC20(rewardToken).safeTransfer(msg.sender, bal);
        }
      }
    }
    return pid;
  }


/// @dev Withdraw from Dahlia and Sushi without caring about rewards
function emergencyBurn2(uint id, uint amount) external nonReentrant returns (uint) {
    if (amount == uint(-1)) {
      amount = balanceOf(msg.sender, id);
    }
    (uint pid, ) = decodeId(id);
    _burn(msg.sender, id, amount);
    chef.emergencyWithdraw(pid, address(this));
    address lpToken = chef.lpToken(pid);
    IERC20(lpToken).safeTransfer(msg.sender, amount);
    return pid;
  }
}