// SPDX-License-Identifier: MIT

pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;


// sliding oracle that uses observations collected to provide moving price averages in the past
interface IUbeswapV1Oracle {

    struct Observation {
        uint timestamp;
        uint price0Cumulative;
        uint price1Cumulative;
    }


  function factory() external pure returns (address);

  function periodSize() external pure returns (uint);

  function pairs() external view returns (address[] memory);

  function observationLength(address pair) external view returns (uint);
  
  function pairFor(address tokenA, address tokenB) external pure returns (address);
  
  function pairForCELO(address tokenA) external pure returns (address);

  function pairForMCELO(address tokenA) external pure returns (address);

  function updatePair(address pair) external returns (bool);

  function update(address tokenA, address tokenB) external returns (bool);

  function addPair(address tokenA, address tokenB) external;

  function work() external;
  
  function lastObservation(address pair) external view
    returns (Observation memory);

  function updateFor(uint i, uint length) external returns (bool updated);

  function workable(address pair) external view returns (bool);

  function workable() external view returns (bool);

  function CELO() external pure returns (address);

  function MCELO() external pure returns (address);
}
