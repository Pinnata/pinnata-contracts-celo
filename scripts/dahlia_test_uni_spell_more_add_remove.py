from brownie import accounts, interface, Contract
from brownie import (
    HomoraBank, ProxyOracle, CoreOracle, UniswapV2Oracle, SimpleOracle, UniswapV2SpellV1, WERC20, SafeBox
)
from .utils import *
import json


def almostEqual(a, b):
    thresh = 0.01
    return a <= b + thresh * abs(b) and a >= b - thresh * abs(b)


def lend(bob, token, safebox):
    # approve dai
    token.approve(safebox, 2**256-1, {'from': bob})
    bob_amt = 10**18
    safebox.deposit(bob_amt, {'from': bob})


def withdraw(bob, token, safebox):
    bob_amt = 10**18
    print(safebox.balanceOf(bob))
    # safebox.withdraw(bob_amt, {'from': bob})
    token.approve(safebox, 0, {'from': bob})


def main():
    alice = accounts.load('alice')
    bob = accounts.load('bob')
    f = open('scripts/dahlia_addresses.json')
    addr = json.load(f)['alfajores']
    
    celo = interface.IERC20Ex(addr['celo'])
    mcusd = interface.IERC20Ex(addr['mcusd'])
    dahlia_bank = HomoraBank.at(addr['dahlia_bank'])
    uniswap_spell = UniswapV2SpellV1.at(addr['uniswap_spell'])
    core_oracle = CoreOracle.at(addr['core_oracle'])
    celo_safebox = SafeBox.at(addr['celo_safebox'])

    lend(bob, celo, celo_safebox)

    celo.approve(dahlia_bank, 2**256-1, {'from': alice})
    mcusd.approve(dahlia_bank, 2**256-1, {'from': alice})

    prevABal = celo.balanceOf(alice)
    prevBBal = mcusd.balanceOf(alice)

    initABal = prevABal
    initBBal = prevBBal

    print('prev A bal', prevABal)
    print('prev B bal', prevBBal)

    # open a position
    dahlia_bank.execute(
        0,
        uniswap_spell,
        uniswap_spell.addLiquidityWERC20.encode_input(
            celo,
            mcusd,
            [10**18, # collateral amount celo
             0, # collateral amount mcusd
             0,
             10**2, # borrow amount celo
             0, # borrow amount mcusd
             0,
             0,
             0],
        ),
        {
            'from': alice, 
        }
    )

    curABal = celo.balanceOf(alice)
    curBBal = mcusd.balanceOf(alice)

    print('alice delta A Bal', curABal - prevABal)
    print('alice delta B Bal', curBBal - prevBBal)

    prevABal = celo.balanceOf(alice)
    prevBBal = mcusd.balanceOf(alice)

    position_id = dahlia_bank.nextPositionId()

    # close the position
    dahlia_bank.execute(
        position_id - 1,
        uniswap_spell,
        uniswap_spell.removeLiquidityWERC20.encode_input(
            celo,
            mcusd,
            [2**256-1, #lp to remove
             0, # lp to keep    
             2**256-1, #repay celo
             0, #repay mcusd
             0,
             0,
             0],
        ),
        {'from': alice}
    )

    curABal = celo.balanceOf(alice)
    curBBal = mcusd.balanceOf(alice)

    finalABal = curABal
    finalBBal = curBBal

    tokenAPrice = core_oracle.getCELOPx(celo)
    tokenBPrice = core_oracle.getCELOPx(mcusd)

    print('alice delta A Bal', curABal - prevABal)
    print('alice delta B Bal', curBBal - prevBBal)

    print('token A price', tokenAPrice)
    print('token B price', tokenBPrice)

    assert almostEqual(tokenAPrice * initABal + tokenBPrice * initBBal,
                       tokenAPrice * finalABal + tokenBPrice * finalBBal), 'too much value lost'

    withdraw(bob, celo, celo_safebox)
    celo.approve(dahlia_bank, 0, {'from': alice})
    mcusd.approve(dahlia_bank, 0, {'from': alice})
    
