from brownie import (
    accounts,
    interface,
    Contract,
    HomoraBank,
    CoreOracle,
    SushiswapSpellV1,
    SafeBox,
    network,
    WComplexTimeRewarder,
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
    sushi = interface.IERC20Ex(addr['sushi'])
    dahlia_bank = Contract.from_abi("HomoraBank", addr.get('dahlia_bank'), HomoraBank.abi)
    sushi_spell = SushiswapSpellV1.at(addr['sushi_spell'])
    core_oracle = CoreOracle.at(addr['core_oracle'])
    rewarder = interface.IComplexTimeRewarder(addr['rewarder'])
    wminichef = addr['wminichef']

    # lend(bob, cusd, cusd_safebox)
    # lend(bob, ceur, ceur_safebox)

    cusd.approve(dahlia_bank, 2**256-1, {'from': alice})
    ceur.approve(dahlia_bank, 2**256-1, {'from': alice})
    cusd.approve(dahlia_bank, 2**256-1, {'from': bob})
    ceur.approve(dahlia_bank, 2**256-1, {'from': bob})

    prevABal = cusd.balanceOf(alice)
    prevBBal = ceur.balanceOf(alice)

    initABal = prevABal
    initBBal = prevBBal

    print('prev A bal', prevABal)
    print('prev B bal', prevBBal)

    prevMRewards = sushi.balanceOf(alice)
    prevM2Rewards = celo.balanceOf(alice)
    bprevMRewards = sushi.balanceOf(bob)
    bprevM2Rewards = celo.balanceOf(bob)

    print(rewarder.poolInfo(1))

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
             10**14,
             10**14,
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
    start = time.time()

    a_position_id = dahlia_bank.nextPositionId()-1
    print('alice', a_position_id)

    # open a position
    dahlia_bank.execute(
        0,
        sushi_spell,
        sushi_spell.addLiquidityWMiniChef.encode_input(
            cusd,
            ceur,
            [
             10**14,
             10**14,
             0,
             10**13,
             10**13,
             0,
             0,
             0
            ],
            3
        ),
        {
            'from': bob, 
        }
    )
    b_position_id = dahlia_bank.nextPositionId()-1
    print('bob', b_position_id)
    # prevBorrow = dahlia_bank.getBorrowCELOValue(position_id)
    # time.sleep(30)
    # dahlia_bank.accrue(cusd, {'from': deployer})
    # dahlia_bank.accrue(ceur, {'from': deployer})
    # postBorrow = dahlia_bank.getBorrowCELOValue(position_id)

    # print(prevBorrow / 10 ** 18, postBorrow / 10 ** 18)
    # assert postBorrow > prevBorrow

    curABal = cusd.balanceOf(alice)
    curBBal = ceur.balanceOf(alice)

    print('alice delta A Bal', curABal - prevABal)
    print('alice delta B Bal', curBBal - prevBBal)

    prevABal = cusd.balanceOf(alice)
    prevBBal = ceur.balanceOf(alice)

    # position_id = dahlia_bank.nextPositionId()-1
    # # prevBorrow = dahlia_bank.getBorrowCELOValue(position_id)
    # time.sleep(30)
    # dahlia_bank.accrue(cusd, {'from': alice})
    # dahlia_bank.accrue(ceur, {'from': alice})
    # postBorrow = dahlia_bank.getBorrowCELOValue(position_id)

    # assert prevBorrow < postBorrow
    time.sleep(80)
    print(rewarder.poolInfo(1))
    print('bob remove')
    dahlia_bank.execute(
        b_position_id,
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
        {'from': bob}
    )

    bpostMRewards = sushi.balanceOf(bob)
    bpostM2Rewards = celo.balanceOf(bob)
    print(bpostMRewards-bprevMRewards)
    print(bpostM2Rewards-bprevM2Rewards)

    print(sushi.balanceOf(wminichef))
    print(celo.balanceOf(wminichef))

    # time.sleep(10)
    print(rewarder.poolInfo(1))
    time.sleep(6)
    # close the position
    print('alice remove')
    dahlia_bank.execute(
        a_position_id,
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
    finish = time.time()
    print(rewarder.poolInfo(1))

    postMRewards = sushi.balanceOf(alice)
    postM2Rewards = celo.balanceOf(alice)
    bpostMRewards = sushi.balanceOf(bob)
    bpostM2Rewards = celo.balanceOf(bob)

    curABal = cusd.balanceOf(alice)
    curBBal = ceur.balanceOf(alice)

    finalABal = curABal
    finalBBal = curBBal

    tokenAPrice = core_oracle.getCELOPx(cusd)
    tokenBPrice = core_oracle.getCELOPx(ceur)

    print('alice delta A Bal', curABal - prevABal)
    print('alice delta B Bal', curBBal - prevBBal)

    print('token A price', tokenAPrice)
    print('token B price', tokenBPrice)

    assert almostEqual(tokenAPrice * initABal + tokenBPrice * initBBal,
                       tokenAPrice * finalABal + tokenBPrice * finalBBal), 'too much value lost'

    # assert postMRewards > prevMRewards
    # assert postM2Rewards > prevM2Rewards
    print(postMRewards-prevMRewards)
    print(postM2Rewards-prevM2Rewards)
    print(bpostMRewards-bprevMRewards)
    print(bpostM2Rewards-bprevM2Rewards)
    print(finish-start)
    print('sushi', sushi.balanceOf(wminichef))
    print('celo', celo.balanceOf(wminichef))
    # assert postCeloRewards > prevCeloRewards

    # celo.approve(dahlia_bank, 0, {'from': alice})
    # cusd.approve(dahlia_bank, 0, {'from': alice})
