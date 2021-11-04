from brownie import (SafeBox, HomoraBank, DahliaLiquidator, WERC20, Contract)
from brownie import accounts, interface, chain
from eth_abi import encode_single
import json

flash_pairs = {
    "0x765DE816845861e75A25fCA122bb6898B8B1282a": ["0x0b655E7D966CB27998af94AA5719ab7BFe07D3b3", "0xD7cb7686Ed438c55149ded0D4762c70AF3D9923a"], #cusd
    "0xD8763CBa276a3738E6DE85b4b3bF5FDed6D6cA73": ["0x0b655E7D966CB27998af94AA5719ab7BFe07D3b3", "0xfED4f77af916B62CB073aD7AD2b2C1794c939023"], #ceur
}

def liquidate(bank, admin, dahlia_liquidator):
    positions = bank.nextPositionId()
    debts = []
    for i in range(1, positions):
        collat = bank.getCollateralCELOValue(i)
        borrow = bank.getBorrowCELOValue(i)
        if collat > 0:
            print("debt", borrow/collat)
            debts.append(borrow/collat)
        if borrow > collat:
            (tokens, debts) = bank.getPositionDebts(i)
            largest = max(debts)
            index_of_largest = debts.index(largest)
            print(tokens, debts, index_of_largest)

            # # find the underlying assets, ubeswap call
            # (_, collToken, collId, _) = bank.getPositionInfo(i)
            # under = interface.IERC20Wrapper(collToken).getUnderlyingToken(collId)
            # if under.lower() != flash_pairs.get(tokens[index_of_largest].lower())[0]:
            #     lp = interface.IUniswapV2Pair(flash_pairs.get(tokens[index_of_largest].lower())[0])
            # else:
            #     lp = interface.IUniswapV2Pair(flash_pairs.get(tokens[index_of_largest].lower())[1])

            # amount0Out = 0
            # amount1Out = 0
            # if lp.token0() == tokens[index_of_largest]:
            #     amount0Out = debts[index_of_largest]
            # elif lp.token1() == tokens[index_of_largest]:
            #     amount1Out = debts[index_of_largest]

            # data = encode_single('uint256', i)
            # print(amount0Out, amount1Out)
            # lp.swap(amount0Out, amount1Out, dahlia_liquidator, data, {"from": admin})
    print(max(debts))

def main():
    admin = accounts.load('dahlia_admin')
    f = open('scripts/dahlia_addresses.json')
    addr = json.load(f)['mainnet']
    bank = Contract.from_abi("HomoraBank", addr.get('dahlia_bank'), HomoraBank.abi)
    dahlia_liquidator = None #addr['dahlia_liquidator']
    liquidate(bank, admin, dahlia_liquidator)
