//SPDX-License-Identifier: Unlicense
pragma solidity 0.6.12;

import 'OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/token/ERC20/IERC20.sol';
import 'OpenZeppelin/openzeppelin-contracts@3.4.0/contracts/math/SafeMath.sol';
import '../interfaces/IBank.sol';
import '../interfaces/IWERC20.sol'; 
import '../interfaces/IUniswapV2Callee.sol';
import '../interfaces/IUniswapV2Pair.sol';
import './libraries/UniswapV2Library.sol';
 

contract ExampleFlashSwap is IUniswapV2Callee {
    using SafeMath for uint; 

    address immutable factory;
    address immutable dahliabank;
    address immutable werc20;

    constructor(address _factory, address _dahliabank, address _werc20) public {
        factory = _factory;
        dahliabank = _dahliabank;
        werc20 = _werc20;
    }

    function uniswapV2Call(address sender, uint amount0, uint amount1, bytes calldata data) external override {
        address tokenBorrow;
        address tokenNotBorrow;
        {
        address token0 = IUniswapV2Pair(msg.sender).token0();
        address token1 = IUniswapV2Pair(msg.sender).token1();
        tokenBorrow = amount0 > 0 ? token0 : token1;
        tokenNotBorrow = amount0 > 0 ? token1 : token0; 
        assert(msg.sender == UniswapV2Library.pairFor(factory, token0, token1)); // ensure that msg.sender is actually a V2 pair
        assert(amount0 == 0 || amount1 == 0); // this strategy is unidirectional
        }

        (uint positionID) = abi.decode(data, (uint));

        // approve
        IERC20(tokenBorrow).approve(dahliabank, uint(-1)); 
        // liquidate call
        IBank(dahliabank).liquidate(positionID, tokenBorrow, uint(-1));
        // get underlying lp
        IWERC20(werc20).burn(msg.sender , uint(-1)); 
        // withdraw lp
        IUniswapV2Pair(msg.sender).burn(address(this)); 

        uint amountNotBorrowIn = 0; 
        uint amountBorrowIn = 0; 
        {
        // return tokens to ubeswap with tip
        uint balanceNotBorrow = IERC20(tokenNotBorrow).balanceOf(msg.sender);
        uint balanceBorrow = IERC20(tokenBorrow).balanceOf(msg.sender);
        (uint reserve0, uint reserve1,) = IUniswapV2Pair(msg.sender).getReserves();
        uint kToGo = reserve0.mul(reserve1).mul(1000**2) > balanceBorrow.mul(balanceNotBorrow).mul(1000**2) ? reserve0.mul(reserve1).mul(1000**2) + 1 - balanceBorrow.mul(balanceNotBorrow).mul(1000**2) : 0;


        // return not borrowed coins first, lower fee
        amountNotBorrowIn = IERC20(tokenNotBorrow).balanceOf(address(this)); 
        kToGo = kToGo > amountNotBorrowIn.mul(997).mul(balanceBorrow).mul(1000) ? kToGo - amountNotBorrowIn.mul(997).mul(balanceBorrow).mul(1000) : 0; 

        // check for completion
        if (kToGo != 0) {
            // return borrowed coins second
            amountBorrowIn = kToGo.div(balanceNotBorrow.mul(1000).add(amountNotBorrowIn.mul(997)));
        }
        }
        // keep rest
        assert(amountBorrowIn <= IERC20(tokenBorrow).balanceOf(address(this)));
        assert(amountNotBorrowIn <= IERC20(tokenNotBorrow).balanceOf(address(this)));
        assert(IERC20(tokenBorrow).transfer(msg.sender, amountBorrowIn));
        assert(IERC20(tokenNotBorrow).transfer(msg.sender, amountNotBorrowIn));
        assert(IERC20(tokenBorrow).transfer(sender, IERC20(tokenBorrow).balanceOf(address(this))));
        assert(IERC20(tokenNotBorrow).transfer(sender, IERC20(tokenNotBorrow).balanceOf(address(this))));
    }
}