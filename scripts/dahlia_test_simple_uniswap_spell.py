from brownie import (
    accounts, ERC20KP3ROracle, UniswapV2Oracle, BalancerPairOracle, ProxyOracle, CoreOracle,
    HomoraBank, CurveOracle, UniswapV2SpellV1, WERC20, WLiquidityGauge, WMasterChef,
    WStakingRewards, SushiswapSpellV1, BalancerSpellV1, CurveSpellV1, UbeswapV1Oracle, SafeBox, SimpleOracle
)
from brownie import interface
from .utils import *


def almostEqual(a, b):
    thresh = 0.01
    return a <= b + thresh * abs(b) and a >= b - thresh * abs(b)


def test_uniswap_spell(uniswap_spell, homora, oracle, celo, cusd):
    alice = accounts[0]

    uniswap_factory = UniswapV2SpellV1.factory({'from': alice})
    uniswap_factory.getPair(celo, cusd, {'from': alice})

    cusd.approve(homora, 2**256-1, {'from': alice})
    celo.approve(homora, 2**256-1, {'from': alice})

    prevABal = cusd.balanceOf(alice)
    prevBBal = celo.balanceOf(alice)
    prevETHBal = alice.balance()

    initABal = prevABal
    initBBal = prevBBal
    initETHBal = prevETHBal

    print('prev A bal', prevABal)
    print('prev B bal', prevBBal)

    # open a position
    homora.execute(
        0,
        uniswap_spell,
        uniswap_spell.addLiquidityWERC20.encode_input(
            cusd,
            celo,
            [10**18,
             10**18,
             0,
             10**18,
             10**18,
             0,
             0,
             0],
        ),
        {'from': alice}
    )

    curABal = cusd.balanceOf(alice)
    curBBal = celo.balanceOf(alice)

    print('alice delta A Bal', curABal - prevABal)
    print('alice delta B Bal', curBBal - prevBBal)

    prevABal = cusd.balanceOf(alice)
    prevBBal = celo.balanceOf(alice)
    prevETHBal = alice.balance()

    position_id = homora.nextPositionId()

    # close the position
    homora.execute(
        position_id - 1,
        uniswap_spell,
        uniswap_spell.removeLiquidityWERC20.encode_input(
            cusd,
            celo,
            [2**256-1,
             0,
             2**256-1,
             2**256-1,
             0,
             0,
             0],
        ),
        {'from': alice}
    )

    curABal = cusd.balanceOf(alice)
    curBBal = celo.balanceOf(alice)
    curETHBal = alice.balance()

    finalABal = curABal
    finalBBal = curBBal
    finalETHBal = curETHBal

    tokenAPrice = oracle.getCELOPx(cusd)
    tokenBPrice = oracle.getCELOPx(celo)
    tokenETHPrice = oracle.getCELOPx('0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE')

    print('alice delta A Bal', curABal - prevABal)
    print('alice delta B Bal', curBBal - prevBBal)
    print('alice delta ETH Bal', curETHBal - prevETHBal)

    print('token A price', tokenAPrice)
    print('token B price', tokenBPrice)
    print('token ETH price', tokenETHPrice)

    assert almostEqual(tokenAPrice * initABal + tokenBPrice * initBBal + tokenETHPrice * initETHBal,
                       tokenAPrice * finalABal + tokenBPrice * finalBBal + tokenETHPrice * finalETHBal), 'too much value lost'


def main():
    deployer = accounts.load('gh')
    uniswap_spell_addr = '0x5F6a662cAc69fE3A0dD22d971F09d49d5AA6fEA9'
    homora_bank_addr = '0xCD9fe42a21DCC22C4BEB11B2e89750870288Fe51'
    core_oracle_addr = '0xc8bFb0364F9cf20ffb9B730267896D94cFea654c'

    uniswap_spell = UniswapV2SpellV1.at(uniswap_spell_addr)
    homora_bank = HomoraBank.at(homora_bank_addr)
    core_oracle = CoreOracle.at(core_oracle_addr)

    test_uniswap_spell(uniswap_spell, homora_bank, core_oracle)