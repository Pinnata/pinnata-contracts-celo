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
    admin = accounts.load('gh')
    alice = accounts.load('alice')
    bob = accounts.load('bob')

    celo_addr = '0xf194afdf50b03e69bd7d057c1aa9e10c9954e4c9'
    mcusd_addr = '0x874069fa1eb16d44d622f2e0ca25eea172369bc1'
    cycelo_addr = '0xB01BCdB6e90C216Ee2Cb15bF97B97283c70932d6'
    dahlia_bank_addr = '0x8772D538785f9dc2a8b1356D4550320E93f4A616'
    uniswap_spell_addr = '0x9F9C8Fe9BC1f28370d947bce6a264aFa4feD5Ec8'
    core_oracle_addr = '0x0286530271720D1B4538e92c7Cc0922D68A053f2'
    celo_safebox_addr = '0x970e26ff0b86145b919e4a54B8a25e4677b0beBC'
    comptroller_addr = '0x115308bBCBd3917033EcE55aC35C92a279A7055D'

    celo = interface.IERC20Ex(celo_addr)
    mcusd = interface.IERC20Ex(mcusd_addr)
    cycelo = interface.IERC20Ex(cycelo_addr)
    dahlia_bank = HomoraBank.at(dahlia_bank_addr)
    uniswap_spell = UniswapV2SpellV1.at(uniswap_spell_addr)
    core_oracle = CoreOracle.at(core_oracle_addr)
    celo_safebox = SafeBox.at(celo_safebox_addr)

    lend(bob, celo, celo_safebox)

    celo.approve(dahlia_bank, 2**256-1, {'from': alice})
    mcusd.approve(dahlia_bank, 2**256-1, {'from': alice})
    celo.approve(celo_safebox_addr, 2**256-1, {'from': alice})
    celo.approve(cycelo, 2**256-1, {'from': alice})

    prevABal = celo.balanceOf(alice)
    prevBBal = mcusd.balanceOf(alice)
    prevETHBal = alice.balance()

    initABal = prevABal
    initBBal = prevBBal
    initETHBal = prevETHBal

    print('prev A bal', prevABal)
    print('prev B bal', prevBBal)

    print('safebox celo bal', celo_safebox.balanceOf(bob, {'from': admin}))

    print('homora cycelo bal', cycelo.balanceOf(dahlia_bank_addr, {'from': admin}))

    print('homora cycelo bal', cycelo.balanceOf(celo_safebox_addr, {'from': admin}))

    print('credit limit', interface.IComptroller(comptroller_addr).creditLimits(dahlia_bank_addr, {'from': admin}))

    # open a position
    dahlia_bank.execute(
        0,
        uniswap_spell,
        uniswap_spell.addLiquidityWERC20.encode_input(
            celo,
            mcusd,
            [10**18, # collateral amount celo
             10**18, # collateral amount mcusd
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
    prevETHBal = alice.balance()

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
    curETHBal = alice.balance()

    finalABal = curABal
    finalBBal = curBBal
    finalETHBal = curETHBal

    tokenAPrice = core_oracle.getCELOPx(celo)
    tokenBPrice = core_oracle.getCELOPx(mcusd)
    tokenETHPrice = core_oracle.getCELOPx(celo)

    print('alice delta A Bal', curABal - prevABal)
    print('alice delta B Bal', curBBal - prevBBal)
    print('alice delta ETH Bal', curETHBal - prevETHBal)

    print('token A price', tokenAPrice)
    print('token B price', tokenBPrice)
    print('token ETH price', tokenETHPrice)

    assert almostEqual(tokenAPrice * initABal + tokenBPrice * initBBal + tokenETHPrice * initETHBal,
                       tokenAPrice * finalABal + tokenBPrice * finalBBal + tokenETHPrice * finalETHBal), 'too much value lost'
