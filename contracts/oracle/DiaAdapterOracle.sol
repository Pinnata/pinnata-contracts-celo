pragma solidity 0.6.12;

import 'OpenZeppelin/openzeppelin-contracts@3.4.0/contracts/math/SafeMath.sol';
import '../Governable.sol';
import '../../interfaces/IBaseOracle.sol';
import './DIAOracle.sol';

contract DiaAdapterOracle is IBaseOracle, Governable {
  using SafeMath for uint256;

  address public diaOracle;
  uint256 public maxDelay;
  mapping(address => string) private query;

  constructor (address _diaOracle, uint256 _maxDelay) public {
    __Governable__init();
    diaOracle = _diaOracle;
    maxDelay = _maxDelay;
  }

  function setMaxDelay(uint256 _maxDelay) external onlyGov {
    maxDelay = _maxDelay;
  }

  function setQuery(address token, string calldata key) external onlyGov {
    query[token] = key;
  }

  /// @dev Return the value of the given input as CELO per unit, multiplied by 2**112.
  /// @param token The ERC-20 token to check the value.
  function getCELOPx(address token) external view override returns (uint) {
    (uint128 celoPrice, uint128 celoTimestamp) = DIAOracle(diaOracle).getValue("CELO/USD");
    require(celoTimestamp >= block.timestamp.sub(maxDelay), "delayed celo update time");
    (uint128 price, uint128 timestamp) = DIAOracle(diaOracle).getValue(query[token]);
    require(timestamp >= block.timestamp.sub(maxDelay), "delayed update time");
    return uint(price).mul(2**112).div(celoPrice);
  }
}
