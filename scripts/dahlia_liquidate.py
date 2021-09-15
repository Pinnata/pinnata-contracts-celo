from brownie import (SafeBox, HomoraBank, ERC20KP3ROracle, UniswapV2Oracle, WERC20)
from brownie import accounts, interface, chain
from .utils import *
from eth_abi import encode_single
import json

flash_pairs = {
    "0x471ece3750da237f93b8e339c536989b8978a438": ["0xe7b5ad135fa22678f426a381c7748f6a5f2c9e6c", "0xf5b1bc6c9c180b64f5711567b1d6a51a350f8422"] # celo to ube/celo, celo/mcusd
}

def liquidate(bank, admin, dahlia_liquidator):
    positions = bank.nextPositionId()
    for i in range(1, positions):
        collat = bank.getCollateralETHValue(i)
        borrow = bank.getBorrowETHValue(i)
        print("collateral value: ", collat)
        print("borrow value: ", borrow)
        if borrow > collat:
            (tokens, debts) = bank.getPositionDebts(i)
            largest = max(debts)
            index_of_largest = debts.index(largest)
            print(tokens, debts, index_of_largest)

            # find the underlying assets, ubeswap call
            (_, collToken, collId, _) = bank.getPositionInfo(i)
            under = interface.IERC20Wrapper(collToken).getUnderlyingToken(collId)
            if under.lower() != flash_pairs.get(tokens[index_of_largest].lower())[0]:
                lp = interface.IUniswapV2Pair(flash_pairs.get(tokens[index_of_largest].lower())[0])
            else:
                lp = interface.IUniswapV2Pair(flash_pairs.get(tokens[index_of_largest].lower())[1])

            amount0Out = 0
            amount1Out = 0
            if lp.token0() == tokens[index_of_largest]:
                amount0Out = debts[index_of_largest]
            elif lp.token1() == tokens[index_of_largest]:
                amount1Out = debts[index_of_largest]
            else:
                print('shit')
                continue

            data = encode_single('uint256', i)

            print(amount0Out, amount1Out)
            lp.swap(amount0Out, amount1Out, dahlia_liquidator, data, {"from": admin})


def main():
    admin = accounts.load('admin')
    f = open('scripts/dahlia_addresses.json')
    addr = json.load(f)['mainnet']
    bank = HomoraBank.at(addr['dahlia_bank'])
    dahlia_liquidator = addr['liquidator']
    liquidate(bank, admin, dahlia_liquidator)
