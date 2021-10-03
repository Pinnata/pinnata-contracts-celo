from brownie import accounts, interface, Contract
from brownie import (
    HomoraBank,
    MockERC20, CoreOracle, UniswapV2Oracle, SimpleOracle, UniswapV2SpellV1, WERC20, SafeBox, WStakingRewards, network
)
import json
import time

network.gas_limit(8000000)


def almostEqual(a, b):
    thresh = 0.01
    return a <= b + thresh * abs(b) and a >= b - thresh * abs(b)


def lend(bob, token, safebox):
    token.approve(safebox, 2**256-1, {'from': bob})

    bob_amt = 10**15
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

    prevRewards = mock.balanceOf(alice)

    position_id = dahlia_bank.nextPositionId()-1
    prevBorrow = dahlia_bank.getBorrowCELOValue(position_id)
    dahlia_bank.accrue(cusd, {'from': deployer})
    dahlia_bank.accrue(celo, {'from': deployer})
    print(prevBorrow/10**10)
    print(1.5*1.3 + (9/6)*1.1)

    collat = dahlia_bank.getCollateralCELOValue(position_id)
    borrow = dahlia_bank.getBorrowCELOValue(position_id)
    print("collateral value: ", collat)
    print("borrow value: ", borrow)

    print(dahlia_bank.getPositionDebts(position_id))

    # close the position
    dahlia_bank.execute(
        position_id,
        uniswap_spell,
        uniswap_spell.removeLiquidityWStakingRewards.encode_input(
            celo,
            cusd,
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

    print(prevRewards)
    print(postRewards)
