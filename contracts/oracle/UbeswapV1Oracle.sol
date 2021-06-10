// SPDX-License-Identifier: MIT

pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

import 'OpenZeppelin/openzeppelin-contracts@3.4.0/contracts/math/SafeMath.sol';
import 'OpenZeppelin/openzeppelin-contracts@3.4.0/contracts/access/Ownable.sol';
import './UniswapV2OracleLibrary.sol';
import '../utils/FixedPoint.sol';
import '../../interfaces/IKeep3rV1Oracle.sol';

// sliding oracle that uses observations collected to provide moving price averages in the past
contract UbeswapV1Oracle is Ownable {
  using SafeMath for uint;
  using FixedPoint for *;

  struct Observation {
    uint timestamp;
    uint price0Cumulative;
    uint price1Cumulative;
  }
  
  address public constant factory = 0x62d5b84bE28a183aBB507E125B384122D2C25fAE;
  // this is redundant with granularity and windowSize, but stored for gas savings & informational purposes.
  uint public constant periodSize = 1800; // 30 minutes

  address[] internal _pairs;
  mapping(address => bool) internal _known;

  function pairs() external view returns (address[] memory) {
    return _pairs;
  }

  mapping(address => Observation[]) public observations;
  
  function observationLength(address pair) external view returns (uint) {
    return observations[pair].length;
  }
  
  function pairFor(address tokenA, address tokenB) external pure returns (address) {
    return UniswapV2Library.pairFor(factory, tokenA, tokenB);
  }
  
  function pairForCELO(address tokenA) external pure returns (address) {
    return UniswapV2Library.pairFor(factory, tokenA, CELO());
  }

  function updatePair(address pair) external onlyOwner returns (bool) {
    return _update(pair);
  }

  function update(address tokenA, address tokenB) external onlyOwner returns (bool) {
    address pair = UniswapV2Library.pairFor(factory, tokenA, tokenB);
    return _update(pair);
  }

  function addPair(address tokenA, address tokenB) onlyOwner external {
    address pair = UniswapV2Library.pairFor(factory, tokenA, tokenB);
    require(!_known[pair], "known");
    _known[pair] = true;
    _pairs.push(pair);

    (uint price0Cumulative, uint price1Cumulative,) = UniswapV2OracleLibrary.currentCumulativePrices(pair);
    observations[pair].push(Observation(block.timestamp, price0Cumulative, price1Cumulative));
  }

  function work() public onlyOwner {
    bool worked = _updateAll();
    require(worked, "UniswapV2Oracle: !work");
  }
  
  function lastObservation(address pair) public view returns (Observation memory) {
    return observations[pair][observations[pair].length-1];
  }

  function _updateAll() internal returns (bool updated) {
    for (uint i = 0; i < _pairs.length; i++) {
      if (_update(_pairs[i])) {
        updated = true;
      }
    }
  }

  function updateFor(uint i, uint length) external onlyOwner returns (bool updated) {
    for (; i < length; i++) {
      if (_update(_pairs[i])) {
        updated = true;
      }
    }
  }

  function workable(address pair) public view returns (bool) {
    return (block.timestamp - lastObservation(pair).timestamp) > periodSize;
  }

  function workable() external view returns (bool) {
    for (uint i = 0; i < _pairs.length; i++) {
      if (workable(_pairs[i])) {
        return true;
      }
    }
    return false;
  }

  function _update(address pair) internal returns (bool) {
    // we only want to commit updates once per period (i.e. windowSize / granularity)
    Observation memory _point = lastObservation(pair);
    uint timeElapsed = block.timestamp - _point.timestamp;
    if (timeElapsed > periodSize) {
      (uint price0Cumulative, uint price1Cumulative,) = UniswapV2OracleLibrary.currentCumulativePrices(pair);
      observations[pair].push(Observation(block.timestamp, price0Cumulative, price1Cumulative));
      return true;
    }
    return false;
  }

  function computeAmountOut(
    uint priceCumulativeStart, uint priceCumulativeEnd,
    uint timeElapsed, uint amountIn
  ) private pure returns (uint amountOut) {
    // overflow is desired.
    FixedPoint.uq112x112 memory priceAverage = FixedPoint.uq112x112(
      uint224((priceCumulativeEnd - priceCumulativeStart) / timeElapsed)
    );
    amountOut = priceAverage.mul(amountIn).decode144();
  }

  function CELO() public pure returns (address) {
    uint256 chainId = computeChainId();
    if (chainId == 42220) {
      return 0x471EcE3750Da237f93B8E339c536989b8978a438;
    } else if (chainId == 44787) {
      return 0xF194afDf50B03e69Bd7D057c1Aa9e10c9954E4C9;
    }
    return address(0);
  }

  function computeChainId() internal pure returns (uint256) {
    uint256 chainId;
    assembly {
      chainId := chainid()
    }
    return chainId;
  }
}
