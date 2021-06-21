from brownie import accounts, interface, Contract
from brownie import (
    HomoraBank, ProxyOracle, CoreOracle, UniswapV2Oracle, SimpleOracle, UniswapV2SpellV1, WERC20, SafeBox
)
from .utils import *


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
    safebox.withdraw(bob_amt, {'from': bob})


def main():
    alice = accounts.load('alice')
    bob = accounts.load('bob')

    celo_addr = '0xf194afdf50b03e69bd7d057c1aa9e10c9954e4c9'
    cusd_addr = '0x874069fa1eb16d44d622f2e0ca25eea172369bc1'
    cycelo_addr = '0x9Ce844b3A315FE2CBB22b88B3Eb0921dD7a2e018'
    cycusd_addr = '0xE5283EAE77252275e6207AC25AAF7A0A4004EEFe'
    dahlia_bank_addr = '0x0460878568C92D877f5544a2F3a1523E6c2bB1CA'
    uniswap_spell_addr = '0xe53ef2fC19F8e905F372432834eED212C692A8F9'
    core_oracle_addr = '0x384f6e069aC3726E1894A30D0d46021c5f5E8acA'
    celo_safebox_addr = '0x47c91f227d04B19E43604F3141779f91feD4f8ad'
    cusd_safebox_addr = '0x2FF09993ebA7292fb93d3F2F87ec498B5c361c64'

    celo = interface.IERC20Ex(celo_addr)
    cusd = interface.IERC20Ex(cusd_addr)
    cycelo = interface.IERC20Ex(cycelo_addr)
    cycusd = interface.IERC20Ex(cycusd_addr)
    dahlia_bank = HomoraBank.at(dahlia_bank_addr)
    uniswap_spell = UniswapV2SpellV1.at(uniswap_spell_addr)
    core_oracle = CoreOracle.at(core_oracle_addr)
    celo_safebox = SafeBox.at(celo_safebox_addr)
    cusd_safebox = SafeBox.at(cusd_safebox_addr)

    lend(bob, celo, celo_safebox)
    lend(bob, cusd, cusd_safebox)

    celo.approve(dahlia_bank, 2**256-1, {'from': alice})
    cusd.approve(dahlia_bank, 2**256-1, {'from': alice})
    celo.approve(cycelo, 2**256-1, {'from': alice})
    cusd.approve(cycusd, 2**256-1, {'from': alice})

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
             10**5,
             10**5,
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
             0,
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
