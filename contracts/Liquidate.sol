//SPDX-License-Identifier: Unlicense
pragma solidity 0.6.12;

import 'OpenZeppelin/openzeppelin-contracts@3.4.0/contracts/token/ERC20/IERC20.sol';
import 'OpenZeppelin/openzeppelin-contracts@3.4.0/contracts/math/SafeMath.sol';
import './utils/ERC1155NaiveReceiver.sol';
import '../interfaces/IBank.sol';
import '../interfaces/IWERC20.sol'; 
import '../interfaces/IUniswapV2Callee.sol';
import '../interfaces/IUniswapV2Pair.sol';
import '../interfaces/IUniswapV2Router02.sol';
import '../interfaces/IWStakingRewards.sol';
import '../interfaces/IERC20Wrapper.sol';
import './libraries/UniswapV2Library.sol';
 

contract DahliaLiquidator is IUniswapV2Callee, ERC1155NaiveReceiver {
    using SafeMath for uint; 

    address immutable router;
    address immutable dahliabank;
    address immutable werc20; 

    constructor(address _router, address _dahliabank, address _werc20) public {
        router = _router;
        dahliabank = _dahliabank;
        werc20 = _werc20;
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

        // Liquidate position
        IUniswapV2Pair under; 
        {
            (uint positionID) = abi.decode(data, (uint));
            // collToken is the wrapped contract, collId is the lp address
            (address _, address collToken, uint collId, uint collateralSize) = IBank(dahliabank).getPositionInfo(positionID); 
            // approve
            IERC20(tokenBorrow).approve(dahliabank, uint(-1)); 
            // liquidate call
            IBank(dahliabank).liquidate(positionID, tokenBorrow, uint(-1));
            // get underlying lp
            under = IUniswapV2Pair(IERC20Wrapper(collToken).getUnderlyingToken(collId)); 
            if (collToken == werc20) {
                IWERC20(collToken).burn(address(collId), collateralSize); 
            } else {
                IWStakingRewards(collToken).burn(collId, collateralSize);
            }
            // withdraw lp
            under.transfer(address(under), collateralSize);
            under.burn(address(this));
        }
        uint amountIn = amountOut.mul(1000).div(997).add(1);
        address tokenToSwap;
        
        {
        // How much token borrowed to return with a tip?
        address token0 = under.token0();
        address token1 = under.token1();
        uint bal0 = IERC20(token0).balanceOf(address(this)); 
        uint bal1 = IERC20(token1).balanceOf(address(this)); 
        if (token0 == tokenBorrow) {
            tokenToSwap = token1; 
            uint send = amountIn > bal0 ? bal0 : amountIn; 
            assert(IERC20(tokenBorrow).transfer(msg.sender, send));
            amountIn = amountIn - send;
        } else {
            tokenToSwap = token0;
            uint send = amountIn > bal1 ? bal1 : amountIn;
            assert(IERC20(tokenBorrow).transfer(msg.sender, send));
            amountIn = amountIn - send; 
        }
        require(token0 == tokenBorrow || token1 == tokenBorrow);
        }

        IERC20(tokenToSwap).approve(router, uint(-1)); 
        if (amountIn > 0) {
            address[] memory path = new address[](2);
            path[0] = tokenToSwap;
            path[1] = tokenBorrow;
            IUniswapV2Router02(router).swapTokensForExactTokens(amountIn, uint(-1), path, msg.sender, uint(-1));
        } else {
            assert(IERC20(tokenBorrow).transfer(sender, IERC20(tokenBorrow).balanceOf(address(this)))); 
        }

        assert(IERC20(tokenToSwap).transfer(sender, IERC20(tokenToSwap).balanceOf(address(this))));
    }
}