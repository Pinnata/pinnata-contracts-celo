from brownie import accounts, interface, Contract
from brownie import (
    HomoraBank,
    MockERC20, CoreOracle, UniswapV2Oracle, SimpleOracle, UniswapV2SpellV1, WERC20, SafeBox, WStakingRewards, network
)
import json
import time

network.gas_limit(8000000)
import time


def almostEqual(a, b):
    thresh = 0.01
    return a <= b + thresh * abs(b) and a >= b - thresh * abs(b)


def lend(bob, token, safebox):
    token.approve(safebox, 2**256-1, {'from': bob})

    bob_amt = 10**18
    safebox.deposit(bob_amt, {'from': bob})


def main():
    deployer = accounts.load('dahlia_admin')
    alice = accounts.load('dahlia_alice')
    bob = accounts.load('dahlia_bob')
    f = open('scripts/dahlia_addresses.json')
    addr = json.load(f)['alfajores']

    celo = interface.IERC20Ex(addr['celo'])
    cusd = interface.IERC20Ex(addr['cusd'])
    dahlia_bank = Contract.from_abi("HomoraBank", addr.get('dahlia_bank'), HomoraBank.abi)
    uniswap_spell = UniswapV2SpellV1.at(addr['uni_spell'])
    core_oracle = CoreOracle.at(addr['core_oracle'])
    celo_safebox = SafeBox.at(addr['dcelo'])
    cusd_safebox = SafeBox.at(addr['dcusd'])
    wstaking = WStakingRewards.at(addr['celo_cusd_wstaking'])
    mock = MockERC20.at(addr['mock'])

    # lend(bob, celo, celo_safebox)
    # lend(bob, cusd, cusd_safebox)

    celo.approve(dahlia_bank, 2**256-1, {'from': alice})
    cusd.approve(dahlia_bank, 2**256-1, {'from': alice})

    prevABal = celo.balanceOf(alice)
    prevBBal = cusd.balanceOf(alice)

    initABal = prevABal
    initBBal = prevBBal

    print('prev A bal', prevABal)
    print('prev B bal', prevBBal)

    prevRewards = mock.balanceOf(alice)

    # open a position
    dahlia_bank.execute(
        0,
        uniswap_spell,
        uniswap_spell.addLiquidityWStakingRewards.encode_input(
            cusd,
            celo,
            [
             6*10**16,
             10**16,
             0,
             9*10**16,
             1.5*10**16,
             0,
             0,
             0
            ],
            wstaking
        ),
        {
            'from': alice, 
        }
    )

    position_id = dahlia_bank.nextPositionId()-1
    prevBorrow = dahlia_bank.getBorrowCELOValue(position_id)
    time.sleep(30)
    dahlia_bank.accrue(cusd, {'from': deployer})
    dahlia_bank.accrue(celo, {'from': deployer})
    postBorrow = dahlia_bank.getBorrowCELOValue(position_id)

    assert prevBorrow < postBorrow

    curABal = celo.balanceOf(alice)
    curBBal = cusd.balanceOf(alice)

    print('alice delta A Bal', curABal - prevABal)
    print('alice delta B Bal', curBBal - prevBBal)

    prevABal = celo.balanceOf(alice)
    prevBBal = cusd.balanceOf(alice)

    position_id = dahlia_bank.nextPositionId()-1
    # prevBorrow = dahlia_bank.getBorrowCELOValue(position_id)
    time.sleep(30)
    dahlia_bank.accrue(cusd, {'from': alice})
    dahlia_bank.accrue(celo, {'from': alice})
    # postBorrow = dahlia_bank.getBorrowCELOValue(position_id)

    # assert prevBorrow < postBorrow

    # close the position
    dahlia_bank.execute(
        position_id,
        uniswap_spell,
        uniswap_spell.removeLiquidityWStakingRewards.encode_input(
            cusd,
            celo,
            [2**256-1,
             0,
             2**256-1,
             2**256-1,
             0,
             0,
             0],
            wstaking
        ),
        {'from': alice}
    )

    postRewards = mock.balanceOf(alice)

    curABal = celo.balanceOf(alice)
    curBBal = cusd.balanceOf(alice)

    finalABal = curABal
    finalBBal = curBBal

    tokenAPrice = core_oracle.getCELOPx(celo)
    tokenBPrice = core_oracle.getCELOPx(cusd)

    print('alice delta A Bal', curABal - prevABal)
    print('alice delta B Bal', curBBal - prevBBal)

    print('token A price', tokenAPrice)
    print('token B price', tokenBPrice)

    assert almostEqual(tokenAPrice * initABal + tokenBPrice * initBBal,
                       tokenAPrice * finalABal + tokenBPrice * finalBBal), 'too much value lost'

    assert postRewards > prevRewards

    # celo.approve(dahlia_bank, 0, {'from': alice})
    # cusd.approve(dahlia_bank, 0, {'from': alice})
