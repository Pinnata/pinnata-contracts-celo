from brownie import accounts, interface, Contract
from brownie import (
    HomoraBank, ProxyOracle, CoreOracle, UniswapV2Oracle, SimpleOracle, UniswapV2SpellV1, WERC20, WMasterChef
)
from .utils import *


def almostEqual(a, b):
    thresh = 0.01
    return a <= b + thresh * abs(b) and a >= b - thresh * abs(b)


def main():
    alice = accounts.load('alice')

    celo_addr = '0xf194afdf50b03e69bd7d057c1aa9e10c9954e4c9'
    cusd_addr = '0x874069fa1eb16d44d622f2e0ca25eea172369bc1'
    dahlia_bank_addr = '0x8772D538785f9dc2a8b1356D4550320E93f4A616'
    uniswap_spell_addr = '0x9F9C8Fe9BC1f28370d947bce6a264aFa4feD5Ec8'
    core_oracle_addr = '0x0286530271720D1B4538e92c7Cc0922D68A053f2'

    celo = interface.IERC20Ex(celo_addr)
    cusd = interface.IERC20Ex(cusd_addr)
    dahlia_bank = HomoraBank.at(dahlia_bank_addr)
    uniswap_spell = UniswapV2SpellV1.at(uniswap_spell_addr)
    core_oracle = CoreOracle.at(core_oracle_addr)

    celo.approve(dahlia_bank, 2**256-1, {'from': alice})
    cusd.approve(dahlia_bank, 2**256-1, {'from': alice})

    prevABal = celo.balanceOf(alice)
    prevBBal = cusd.balanceOf(alice)
    prevETHBal = alice.balance()

    initABal = prevABal
    initBBal = prevBBal
    initETHBal = prevETHBal

    print('prev A bal', prevABal)
    print('prev B bal', prevBBal)

    # open a position
    dahlia_bank.execute(
        0,
        uniswap_spell,
        uniswap_spell.addLiquidityWERC20.encode_input(
            celo,
            cusd,
            [10**9,
             10**9,
             0,
             0,
             0,
             0,
             0,
             0],
        ),
        {'from': alice}
    )

    curABal = celo.balanceOf(alice)
    curBBal = cusd.balanceOf(alice)

    print('alice delta A Bal', curABal - prevABal)
    print('alice delta B Bal', curBBal - prevBBal)

    prevABal = celo.balanceOf(alice)
    prevBBal = cusd.balanceOf(alice)
    prevETHBal = alice.balance()

    position_id = dahlia_bank.nextPositionId()

    # close the position
    dahlia_bank.execute(
        position_id - 1,
        uniswap_spell,
        uniswap_spell.removeLiquidityWERC20.encode_input(
            celo,
            cusd,
            [2**256-1,
             0,
             0,
             2**256-1,
             0,
             0,
             0],
        ),
        {'from': alice}
    )

    curABal = celo.balanceOf(alice)
    curBBal = cusd.balanceOf(alice)
    curETHBal = alice.balance()

    finalABal = curABal
    finalBBal = curBBal
    finalETHBal = curETHBal

    tokenAPrice = core_oracle.getCELOPx(celo)
    tokenBPrice = core_oracle.getCELOPx(cusd)
    tokenETHPrice = core_oracle.getCELOPx(celo)

    print('alice delta A Bal', curABal - prevABal)
    print('alice delta B Bal', curBBal - prevBBal)
    print('alice delta ETH Bal', curETHBal - prevETHBal)

    print('token A price', tokenAPrice)
    print('token B price', tokenBPrice)
    print('token ETH price', tokenETHPrice)

    assert almostEqual(tokenAPrice * initABal + tokenBPrice * initBBal + tokenETHPrice * initETHBal,
                       tokenAPrice * finalABal + tokenBPrice * finalBBal + tokenETHPrice * finalETHBal), 'too much value lost'
