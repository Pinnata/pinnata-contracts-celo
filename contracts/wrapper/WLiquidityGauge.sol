// SPDX-License-Identifier: MIT

pragma solidity 0.6.12;

import 'OpenZeppelin/openzeppelin-contracts@3.4.0/contracts/token/ERC1155/ERC1155.sol';
import 'OpenZeppelin/openzeppelin-contracts@3.4.0/contracts/token/ERC20/SafeERC20.sol';
import 'OpenZeppelin/openzeppelin-contracts@3.4.0/contracts/utils/ReentrancyGuard.sol';

import '../Governable.sol';
import '../utils/HomoraMath.sol';
import '../../interfaces/IERC20Wrapper.sol';
import '../../interfaces/ILiquidityGauge.sol';

interface ILiquidityGaugeMinter {
  function mint(address gauge) external;
}

contract WLiquidityGauge is ERC1155('WLiquidityGauge'), ReentrancyGuard, IERC20Wrapper, Governable {
  using SafeMath for uint;
  using HomoraMath for uint;
  using SafeERC20 for IERC20;

  struct GaugeInfo {
    ILiquidityGauge impl; // Gauge implementation
    uint accMobiPerShare; // Accumulated MOBI per share
    uint id; // Pool Id
  }

  IERC20 public immutable mobi; // MOBI token
  uint nextPoolId; // The next pool id to assign
  mapping(address => GaugeInfo) public gauges; // Mapping from pool id to (mapping from gauge id to GaugeInfo)
  mapping(uint => GaugeInfo) public idToGauges; // Mapping from pool id to Gauge Info

  constructor(IERC20 _mobi) public {
    __Governable__init();
    mobi = _mobi;
    nextPoolId = 0;
  }

  /// @dev Encode pid, mobiPerShare to a ERC1155 token id
  /// @param pid Curve pool id (10-bit)
  /// @param mobiPerShare MOBI amount per share, multiplied by 1e18 (240-bit)
  function encodeId(
    uint pid,
    uint mobiPerShare
  ) public pure returns (uint) {
    require(pid < (1 << 10), 'bad pid');
    require(mobiPerShare < (1 << 240), 'bad mobi per share');
    return (pid << 240) | mobiPerShare;
  }

  /// @dev Decode ERC1155 token id to pid, mobiPerShare
  /// @param id Token id to decode
  function decodeId(uint id)
    public
    pure
    returns (
      uint pid,
      uint mobiPerShare
    )
  {
    pid = id >> 240; // First 16 bits
    mobiPerShare = id & ((1 << 240) - 1); // Last 240 bits
  }

  /// @dev Get underlying ERC20 token of ERC1155 given pid
  /// @param pid pool id
  function getUnderlyingTokenFromId(uint pid) public view returns (address) {
    ILiquidityGauge impl = idToGauges[pid].impl;
    require(address(impl) != address(0), 'no gauge');
    return impl.lp_token();
  }

  /// @dev Get underlying ERC20 token of ERC1155 given token id
  /// @param id Token id
  function getUnderlyingToken(uint id) external view override returns (address) {
    (uint pid,, ) = decodeId(id);
    return getUnderlyingTokenFromIds(pid);
  }

  /// @dev Return the conversion rate from ERC-1155 to ERC-20, multiplied by 2**112.
  function getUnderlyingRate(uint) external view override returns (uint) {
    return 2**112;
  }

  /// @dev Register gauge to storage given pool address and gauge address
  /// @param poolAddress Pool address
  /// @param gaugeAddress Gauge address
  function registerGauge(address poolAddress, address gaugeAddress) external onlyGov {
    require(address(gauges[poolAddress].impl) == address(0), 'gauge already exists');
    IERC20 lpToken = IERC20(ILiquidityGauge(gaugeAddress).lp_token());
    lpToken.approve(gaugeAddress, 0);
    lpToken.approve(gaugeAddress, uint(-1));
    GaugeInfo memory info = GaugeInfo({impl: ILiquidityGauge(gaugeAddress), accMobiPerShare: 0, id: nextPoolId});
    gauges[poolAddress] = info;
    idToGauges[nextPoolId++] = info;
  }

  /// @dev Mint ERC1155 token for the given ERC20 token
  /// @param poolAddress Pool address
  /// @param amount Token amount to wrap
  function mint(
    address poolAddress,
    uint amount
  ) external nonReentrant returns (uint) {
    GaugeInfo storage gauge = gauges[poolAddress];
    ILiquidityGauge impl = gauge.impl;
    require(address(impl) != address(0), 'gauge not registered');
    mintMobi(gauge);
    IERC20 lpToken = IERC20(impl.lp_token());
    lpToken.safeTransferFrom(msg.sender, address(this), amount);
    impl.deposit(amount);
    uint id = encodeId(gauge.id, gauge.accMobiPerShare);
    _mint(msg.sender, id, amount, '');
    return id;
  }

  /// @dev Burn ERC1155 token to redeem ERC20 token back
  /// @param id Token id to burn
  /// @param amount Token amount to burn
  function burn(uint id, uint amount) external nonReentrant returns (uint) {
    if (amount == uint(-1)) {
      amount = balanceOf(msg.sender, id);
    }
    (uint pid, uint stMobiPerShare) = decodeId(id);
    _burn(msg.sender, id, amount);
    GaugeInfo storage gauge = idToGauges[pid];
    ILiquidityGauge impl = gauge.impl;
    require(address(impl) != address(0), 'gauge not registered');
    mintMobi(gauge);
    impl.withdraw(amount);
    IERC20(impl.lp_token()).safeTransfer(msg.sender, amount);
    uint stMobi = stMobiPerShare.mul(amount).divCeil(1e18);
    uint enMobi = gauge.accMobiPerShare.mul(amount).div(1e18);
    if (enMobi > stMobi) {
      mobi.safeTransfer(msg.sender, enMobi.sub(stMobi));
    }
    return pid;
  }

  /// @dev Mint CRV reward for curve gauge
  /// @param gauge Curve gauge to mint reward
  function mintMobi(GaugeInfo storage gauge) internal {
    ILiquidityGauge impl = gauge.impl;
    uint balanceBefore = mobi.balanceOf(address(this));
    ILiquidityGaugeMinter(impl.minter()).mint(address(impl));
    uint balanceAfter = mobi.balanceOf(address(this));
    uint gain = balanceAfter.sub(balanceBefore);
    uint supply = impl.balanceOf(address(this));
    if (gain > 0 && supply > 0) {
      gauge.accMobiPerShare = gauge.accMobiPerShare.add(gain.mul(1e18).div(supply));
    }
  }
}