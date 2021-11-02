from brownie import (
    accounts,
    interface,
    Contract,
    HomoraBank,
    CoreOracle,
    SushiswapSpellV1,
    SafeBox,
    network
)
import json
import time

network.gas_limit(8000000)


def almostEqual(a, b):
    thresh = 0.01
    return a <= b + thresh * abs(b) and a >= b - thresh * abs(b)


def lend(bob, token, safebox):
    token.approve(safebox, 2**256-1, {'from': bob})

    bob_amt = 10**17
    safebox.deposit(bob_amt, {'from': bob})


def main():
    deployer = accounts.load('dahlia_admin')
    alice = accounts.load('dahlia_alice')
    bob = accounts.load('dahlia_bob')
    f = open('scripts/dahlia_addresses.json')
    addr = json.load(f)['mainnet']

    celo = interface.IERC20Ex(addr['celo'])
    cusd = interface.IERC20Ex(addr['cusd'])
    ceur = interface.IERC20Ex(addr['ceur'])
    dahlia_bank = Contract.from_abi("HomoraBank", addr.get('dahlia_bank'), HomoraBank.abi)
    sushi_spell = SushiswapSpellV1.at(addr['sushi_spell'])
    core_oracle = CoreOracle.at(addr['core_oracle'])
    cusd_safebox = SafeBox.at(addr['dcusd'])
    ceur_safebox = SafeBox.at(addr['dceur'])
    sushi = interface.IERC20Ex(addr['sushi'])

    # lend(bob, cusd, cusd_safebox)
    # lend(bob, ceur, ceur_safebox)

    # cusd.approve(dahlia_bank, 2**256-1, {'from': alice})
    # ceur.approve(dahlia_bank, 2**256-1, {'from': alice})

    prevBBal = cusd.balanceOf(alice)
    prevABal = ceur.balanceOf(alice)

    initABal = prevABal
    initBBal = prevBBal

    print('prev A bal', prevABal)
    print('prev B bal', prevBBal)

    prevRewards = sushi.balanceOf(alice)
    prevCeloRewards = celo.balanceOf(alice)

    # open a position
    dahlia_bank.execute(
        0,
        sushi_spell,
        sushi_spell.addLiquidityWMiniChef.encode_input(
            cusd,
            ceur,
            [
             10**15,
             10**15,
             0,
             10**15,
             10**15,
             0,
             0,
             0
            ],
            3
        ),
        {
            'from': alice, 
        }
    )

    position_id = dahlia_bank.nextPositionId()-1
    # prevBorrow = dahlia_bank.getBorrowCELOValue(position_id)
    # time.sleep(30)
    # dahlia_bank.accrue(cusd, {'from': deployer})
    # dahlia_bank.accrue(ceur, {'from': deployer})
    # postBorrow = dahlia_bank.getBorrowCELOValue(position_id)

    # print(prevBorrow / 10 ** 18, postBorrow / 10 ** 18)
    # assert postBorrow > prevBorrow

    curBBal = cusd.balanceOf(alice)
    curABal = ceur.balanceOf(alice)

    print('alice delta A Bal', curABal - prevABal)
    print('alice delta B Bal', curBBal - prevBBal)

    prevBBal = cusd.balanceOf(alice)
    prevABal = ceur.balanceOf(alice)

    # position_id = dahlia_bank.nextPositionId()-1
    # # prevBorrow = dahlia_bank.getBorrowCELOValue(position_id)
    # time.sleep(30)
    # dahlia_bank.accrue(cusd, {'from': alice})
    # dahlia_bank.accrue(ceur, {'from': alice})
    # postBorrow = dahlia_bank.getBorrowCELOValue(position_id)

    # assert prevBorrow < postBorrow

    # close the position
    dahlia_bank.execute(
        position_id,
        sushi_spell,
        sushi_spell.removeLiquidityWMiniChef.encode_input(
            cusd,
            ceur,
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

    postRewards = sushi.balanceOf(alice)
    postCeloRewards = celo.balanceOf(alice)

    curBBal = cusd.balanceOf(alice)
    curABal = ceur.balanceOf(alice)

    finalABal = curABal
    finalBBal = curBBal

    tokenAPrice = core_oracle.getCELOPx(ceur)
    tokenBPrice = core_oracle.getCELOPx(cusd)

    print('alice delta A Bal', curABal - prevABal)
    print('alice delta B Bal', curBBal - prevBBal)

    print('token A price', tokenAPrice)
    print('token B price', tokenBPrice)

    assert almostEqual(tokenAPrice * initABal + tokenBPrice * initBBal,
                       tokenAPrice * finalABal + tokenBPrice * finalBBal), 'too much value lost'

    assert postRewards > prevRewards
    # assert postCeloRewards > prevCeloRewards

    # celo.approve(dahlia_bank, 0, {'from': alice})
    # cusd.approve(dahlia_bank, 0, {'from': alice})
