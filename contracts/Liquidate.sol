//SPDX-License-Identifier: Unlicense
pragma solidity 0.6.12;

import 'OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/token/ERC20/IERC20.sol';
import 'OpenZeppelin/openzeppelin-contracts@3.4.0/contracts/math/SafeMath.sol';
import './utils/ERC1155NaiveReceiver.sol';
import '../interfaces/IBank.sol';
import '../interfaces/IWERC20.sol'; 
import '../interfaces/IUniswapV2Callee.sol';
import '../interfaces/IUniswapV2Pair.sol';
import '../interfaces/IUniswapV2Router02.sol';
import './libraries/UniswapV2Library.sol';
 

contract DahliaLiquidator is IUniswapV2Callee, ERC1155NaiveReceiver {
    using SafeMath for uint; 

    address immutable router;
    address immutable dahliabank;

    constructor(address _router, address _dahliabank) public {
        router = _router;
        dahliabank = _dahliabank;
    }

    function uniswapV2Call(address sender, uint amount0, uint amount1, bytes calldata data) external override {
        address tokenBorrow;
        uint amountOut;
        {
        address token0 = IUniswapV2Pair(msg.sender).token0();
        address token1 = IUniswapV2Pair(msg.sender).token1();
        if (amount0 > 0) {
            tokenBorrow = token0; 
            amountOut = amount0;
        } else {
            tokenBorrow = token1; 
            amountOut = amount1;
        }
        address factory = IUniswapV2Router02(router).factory();
        assert(msg.sender == UniswapV2Library.pairFor(factory, token0, token1)); // ensure that msg.sender is actually a V2 pair
        assert(amount0 == 0 || amount1 == 0); // this strategy is unidirectional
        }
        (uint positionID) = abi.decode(data, (uint));

        (address _, address collToken, uint collId, uint collateralSize) = IBank(dahliabank).getPositionInfo(positionID); 

        
        // approve
        IERC20(tokenBorrow).approve(dahliabank, uint(-1)); 
        // liquidate call
        IBank(dahliabank).liquidate(positionID, tokenBorrow, uint(-1));
        // get underlying lp
        IWERC20(collToken).burn(address(collId), IWERC20(collToken).balanceOfERC20(address(collId), address(this))); 
        // withdraw lp
        IUniswapV2Pair(address(collId)).transfer(address(collId), collateralSize);

        uint amountIn = amountOut.mul(1000).div(997).add(1);
        address tokenToSwap;
        
        {
        (uint bal0, uint bal1) = IUniswapV2Pair(address(collId)).burn(address(this)); 
        // How much token borrowed to return with a tip?
        address token0 = IUniswapV2Pair(address(collId)).token0();
        address token1 = IUniswapV2Pair(address(collId)).token1();
        if (token0 == tokenBorrow) {
            tokenToSwap = token1; 
            amountIn = amountIn > bal0 ? amountIn - bal0 : 0; 
            assert(IERC20(tokenBorrow).transfer(msg.sender, bal0));
        } else {
            tokenToSwap = token0;
            amountIn = amountIn > bal1 ? amountIn - bal1 : 0;
            assert(IERC20(tokenBorrow).transfer(msg.sender, bal1));
        }
        require(token0 == tokenBorrow || token1 == tokenBorrow);
        }

        IERC20(tokenToSwap).approve(router, uint(-1)); 

        {
        address[] memory path = new address[](2);
        path[0] = tokenToSwap;
        path[1] = tokenBorrow;
        IUniswapV2Router02(router).swapTokensForExactTokens(amountIn, uint(-1), path, msg.sender, uint(-1));
        }

        assert(IERC20(tokenToSwap).transfer(sender, IERC20(tokenToSwap).balanceOf(address(this))));
    }
}