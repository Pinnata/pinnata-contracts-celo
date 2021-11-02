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
    addr = json.load(f)['alfajores']

    celo = interface.IERC20Ex(addr['celo'])
    cusd = interface.IERC20Ex(addr['cusd'])
    mock = interface.IERC20Ex(addr['mock'])
    mock2 = interface.IERC20Ex(addr['mock2'])
    dahlia_bank = Contract.from_abi("HomoraBank", addr.get('dahlia_bank'), HomoraBank.abi)
    sushi_spell = SushiswapSpellV1.at(addr['sushi_spell'])
    core_oracle = CoreOracle.at(addr['core_oracle'])
    rewarder = interface.IComplexTimeRewarder(addr['rewarder'])
    wminichef = addr['wminichef']

    # lend(bob, cusd, cusd_safebox)
    # lend(bob, ceur, ceur_safebox)

    # cusd.approve(dahlia_bank, 2**256-1, {'from': alice})
    # ceur.approve(dahlia_bank, 2**256-1, {'from': alice})

    prevBBal = cusd.balanceOf(alice)
    prevABal = celo.balanceOf(alice)

    initABal = prevABal
    initBBal = prevBBal

    print('prev A bal', prevABal)
    print('prev B bal', prevBBal)

    prevMRewards = mock.balanceOf(alice)
    prevM2Rewards = mock2.balanceOf(alice)
    bprevMRewards = mock.balanceOf(bob)
    bprevM2Rewards = mock2.balanceOf(bob)

    print(rewarder.poolInfo(1))

    # open a position
    dahlia_bank.execute(
        0,
        sushi_spell,
        sushi_spell.addLiquidityWMiniChef.encode_input(
            cusd,
            celo,
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
            1
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
            celo,
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
            1
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

    curBBal = cusd.balanceOf(alice)
    curABal = celo.balanceOf(alice)

    print('alice delta A Bal', curABal - prevABal)
    print('alice delta B Bal', curBBal - prevBBal)

    prevBBal = cusd.balanceOf(alice)
    prevABal = celo.balanceOf(alice)

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
            celo,
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

    bpostMRewards = mock.balanceOf(bob)
    bpostM2Rewards = mock2.balanceOf(bob)
    print(bpostMRewards-bprevMRewards)
    print(bpostM2Rewards-bprevM2Rewards)

    print(mock.balanceOf(wminichef))
    print(mock2.balanceOf(wminichef))

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
    finish = time.time()
    print(rewarder.poolInfo(1))

    postMRewards = mock.balanceOf(alice)
    postM2Rewards = mock2.balanceOf(alice)
    bpostMRewards = mock.balanceOf(bob)
    bpostM2Rewards = mock2.balanceOf(bob)

    curBBal = cusd.balanceOf(alice)
    curABal = celo.balanceOf(alice)

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

    assert postMRewards > prevMRewards
    assert postM2Rewards > prevM2Rewards
    print(postMRewards-prevMRewards)
    print(postM2Rewards-prevM2Rewards)
    print(bpostMRewards-bprevMRewards)
    print(bpostM2Rewards-bprevM2Rewards)
    print(finish-start)
    print('mock', mock.balanceOf(wminichef))
    print('mock2', mock2.balanceOf(wminichef))
    # assert postCeloRewards > prevCeloRewards

    # celo.approve(dahlia_bank, 0, {'from': alice})
    # cusd.approve(dahlia_bank, 0, {'from': alice})
