// SPDX-License-Identifier: MIT

pragma solidity 0.6.12;

import 'OpenZeppelin/openzeppelin-contracts@3.4.0/contracts/token/ERC20/IERC20.sol';

import './BasicSpell.sol';
import '../../interfaces/IBank.sol';

contract HouseHoldSpell is BasicSpell {
  constructor(
    IBank _bank,
    address _werc20,
    address _celo
  ) public BasicSpell(_bank, _werc20, _celo) {}

  function borrow(address token, uint amount) external {
    doBorrow(token, amount);
    doRefund(token);
  }

  function repay(address token, uint amount) external {
    doTransmit(token, amount);
    doRepay(token, IERC20(token).balanceOf(address(this)));
  }

  function putCollateral(address token, uint amount) external {
    doTransmit(token, amount);
    doPutCollateral(token, IERC20(token).balanceOf(address(this)));
  }

  function takeCollateral(address token, uint amount) external {
    doTakeCollateral(token, amount);
    doRefund(token);
  }
}
