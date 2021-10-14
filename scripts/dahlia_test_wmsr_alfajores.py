from brownie import (
    accounts,
    WMStakingRewards, 
    interface,
    network,
    SafeBox,
    Contract,
    HomoraBank,
    UniswapV2SpellV1,
)

import json
import time

network.gas_limit(8000000)

def lend(bob, token, safebox):
    token.approve(safebox, 2**256-1, {'from': bob})

    bob_amt = 10**18
    safebox.deposit(bob_amt, {'from': bob})

def main():
    alice = accounts.load('dahlia_alice')
    bob = accounts.load('dahlia_bob')

    with open('scripts/dahlia_addresses.json', 'r') as f:
        addr = json.load(f)

    alfajores_addr = addr.get('alfajores')

    celo = interface.IERC20Ex(alfajores_addr.get('celo'))
    cusd = interface.IERC20Ex(alfajores_addr.get('cusd'))
    ceur = interface.IERC20Ex(alfajores_addr.get('ceur'))
    mock = interface.IERC20Ex(alfajores_addr.get('mock'))
    mock2 = interface.IERC20Ex(alfajores_addr.get('mock2'))

    celo_safebox = SafeBox.at(alfajores_addr['dcelo'])
    cusd_safebox = SafeBox.at(alfajores_addr['dcusd'])
    dahlia_bank = Contract.from_abi("HomoraBank", alfajores_addr.get('dahlia_bank'), HomoraBank.abi)
    ufactory = interface.IUniswapV2Factory(alfajores_addr.get('ufactory'))
    ubeswap_msr_spell = UniswapV2SpellV1.at(alfajores_addr['ubeswap_msr_spell'])

    celo_cusd_wmstaking = WMStakingRewards.at(alfajores_addr.get('celo_cusd_wmstaking'))
    celo_ceur_wmstaking = WMStakingRewards.at(alfajores_addr.get('celo_ceur_wmstaking'))
    cusd_ceur_wmstaking = WMStakingRewards.at(alfajores_addr.get('cusd_ceur_wmstaking'))

    celo_cusd_lp = interface.IERC20Ex(ufactory.getPair(celo, cusd))
    celo_ceur_lp = interface.IERC20Ex(ufactory.getPair(celo, ceur))
    cusd_ceur_lp = interface.IERC20Ex(ufactory.getPair(cusd, ceur))

    aPrevGROW = mock.balanceOf(alice)
    aPrevMOM = mock2.balanceOf(alice)
    bPrevGROW = mock.balanceOf(bob)
    bPrevMOM = mock2.balanceOf(bob)

    lend(bob, celo, celo_safebox)
    lend(bob, cusd, cusd_safebox)

    aPrevLP = celo_cusd_lp.balanceOf(alice)
    bPrevLP = celo_cusd_lp.balanceOf(bob)

    prevABal = celo.balanceOf(alice)
    prevBBal = cusd.balanceOf(alice)

    celo.approve(dahlia_bank, 2**256-1, {'from': alice})
    cusd.approve(dahlia_bank, 2**256-1, {'from': alice})

    prevRewards = mock2.balanceOf(alice)

    # open a position
    dahlia_bank.execute(
        0,
        ubeswap_msr_spell,
        ubeswap_msr_spell.addLiquidityWStakingRewards.encode_input(
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
            celo_cusd_wmstaking
        ),
        {
            'from': alice, 
        }
    )

    position_id = dahlia_bank.nextPositionId()-1
    prevBorrow = dahlia_bank.getBorrowCELOValue(position_id)
    time.sleep(30)
    dahlia_bank.accrue(cusd, {'from': alice})
    dahlia_bank.accrue(celo, {'from': alice})
    postBorrow = dahlia_bank.getBorrowCELOValue(position_id)

    assert prevBorrow < postBorrow

    curABal = celo.balanceOf(alice)
    curBBal = cusd.balanceOf(alice)

    print('alice delta A Bal', curABal - prevABal)
    print('alice delta B Bal', curBBal - prevBBal)

    prevABal = celo.balanceOf(alice)
    prevBBal = cusd.balanceOf(alice)

    # close the position
    dahlia_bank.execute(
        position_id,
        ubeswap_msr_spell,
        ubeswap_msr_spell.removeLiquidityWStakingRewards.encode_input(
            cusd,
            celo,
            [2**256-1,
             0,
             2**256-1,
             2**256-1,
             0,
             0,
             0],
            celo_cusd_wmstaking
        ),
        {'from': alice}
    )

    postRewards = mock2.balanceOf(alice)

    curABal = celo.balanceOf(alice)
    curBBal = cusd.balanceOf(alice)

    # tokenAPrice = core_oracle.getCELOPx(celo)
    # tokenBPrice = core_oracle.getCELOPx(cusd)

    print('alice delta A Bal', curABal - prevABal)
    print('alice delta B Bal', curBBal - prevBBal)

    # print('token A price', tokenAPrice)
    # print('token B price', tokenBPrice)

    # assert almostEqual(tokenAPrice * initABal + tokenBPrice * initBBal,
    #                    tokenAPrice * finalABal + tokenBPrice * finalBBal), 'too much value lost'

    assert postRewards > prevRewards

    # celo.approve(dahlia_bank, 0, {'from': alice})
    # cusd.approve(dahlia_bank, 0, {'from': alice})


    # celo_cusd_wmstaking.mint(3 * 10**10, {'from': alice})

    # time.sleep(30)

    # celo_cusd_wmstaking.mint(10**10, {'from': bob})

    # time.sleep(90)

    # celo_cusd_wmstaking.burn(10, 2**256-1, {'from': bob})
    # celo_cusd_wmstaking.burn(10, 2**256-1, {'from': alice})

    # aPostGROW = mock.balanceOf(alice)
    # aPostMOM = mock2.balanceOf(alice)
    # bPostGROW = mock.balanceOf(bob)
    # bPostMOM = mock2.balanceOf(bob)
    # aPostLP = celo_cusd_lp.balanceOf(alice)
    # bPostLP = celo_cusd_lp.balanceOf(bob)

    # print('alice grow', aPrevGROW, aPostGROW)
    # print('alice mom', aPrevMOM, aPostMOM)
    # print('bob grow', bPrevGROW, bPostGROW)
    # print('bob mom', bPrevMOM, bPostMOM)
    # print('alice lp', aPrevLP, aPostLP)
    # print('bob lp', bPrevLP, bPostLP)

