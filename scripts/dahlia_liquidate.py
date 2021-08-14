from brownie import (SafeBox, HomoraBank, ERC20KP3ROracle, UniswapV2Oracle)
from brownie import accounts, interface, chain
from .utils import *
import json

def liquidate(bank, admin):
    positions = bank.nextPositionId()
    print(positions)
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
            # bank.liquidate(i, tokens[index_of_largest], 2 ** 256 - 1)

    

def main():
    admin = accounts.load('admin')
    f = open('scripts/dahlia_addresses.json')
    addr = json.load(f)['mainnet']
    bank = HomoraBank.at(addr['dahlia_bank'])
    liquidate(bank, admin)
