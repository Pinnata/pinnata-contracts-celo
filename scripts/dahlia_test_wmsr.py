from brownie import (
    accounts,
    WMStakingRewards, 
    interface,
    network,
    SafeBox,
    Contract,
    HomoraBank,
    UniswapV2SpellV1,
    CoreOracle,
)

import json
import time

network.gas_limit(8000000)

def almostEqual(a, b):
    thresh = 0.01
    return a <= b + thresh * abs(b) and a >= b - thresh * abs(b)

def lend(bob, token, safebox):
    token.approve(safebox, 2**256-1, {'from': bob})

    bob_amt = 10**16
    safebox.deposit(bob_amt, {'from': bob})

def main():
    alice = accounts.load('dahlia_alice')
    bob = accounts.load('dahlia_bob')

    with open('scripts/dahlia_addresses.json', 'r') as f:
        addr = json.load(f)

    mainnet_addr = addr.get('mainnet')

    celo = interface.IERC20Ex(mainnet_addr.get('celo'))
    mcusd = interface.IERC20Ex(mainnet_addr.get('mcusd'))
    mceur = interface.IERC20Ex(mainnet_addr.get('mceur'))
    ube = interface.IERC20Ex(mainnet_addr.get('ube'))
    moo = interface.IERC20Ex(mainnet_addr.get('moo'))

    celo_safebox = SafeBox.at(mainnet_addr['dcelo'])
    mcusd_safebox = SafeBox.at(mainnet_addr['dmcusd'])
    mceur_safebox = SafeBox.at(mainnet_addr['dmceur'])
    
    dahlia_bank = Contract.from_abi("HomoraBank", mainnet_addr.get('dahlia_bank'), HomoraBank.abi)
    ufactory = interface.IUniswapV2Factory(mainnet_addr.get('ube_factory'))
    ubeswap_msr_spell = UniswapV2SpellV1.at(mainnet_addr['ubeswap_msr_spell'])
    core_oracle = CoreOracle.at(mainnet_addr['core_oracle'])

    celo_mcusd_wmstaking = WMStakingRewards.at(mainnet_addr.get('celo_mcusd_wmstaking'))
    celo_mceur_wmstaking = WMStakingRewards.at(mainnet_addr.get('celo_mceur_wmstaking'))
    mcusd_mceur_wmstaking = WMStakingRewards.at(mainnet_addr.get('mcusd_mceur_wmstaking'))

    a_prev_ube = ube.balanceOf(alice)
    a_prev_moo = moo.balanceOf(alice)
    b_prev_ube = ube.balanceOf(bob)
    b_prev_moo = moo.balanceOf(bob)

    # lend(bob, celo, celo_safebox)
    # lend(bob, mcusd, mcusd_safebox)
    # lend(bob, mceur, mceur_safebox)

    prevABal = mcusd.balanceOf(alice)
    prevBBal = mceur.balanceOf(alice)

    initABal = prevABal
    initBBal = prevBBal

    # celo.approve(dahlia_bank, 2**256-1, {'from': alice})
    # mcusd.approve(dahlia_bank, 2**256-1, {'from': alice})
    # mceur.approve(dahlia_bank, 2**256-1, {'from': alice})

    # celo.approve(dahlia_bank, 2**256-1, {'from': bob})
    # mcusd.approve(dahlia_bank, 2**256-1, {'from': bob})
    # mceur.approve(dahlia_bank, 2**256-1, {'from': bob})

    print(prevABal, prevBBal)

    # open a position
    dahlia_bank.execute(
        0,
        ubeswap_msr_spell,
        ubeswap_msr_spell.addLiquidityWStakingRewards.encode_input(
            mcusd,
            mceur,
            [
             10**16,
             10**16,
             0,
             10**13,
             10**13,
             0,
             0,
             0
            ],
            mcusd_mceur_wmstaking
        ),
        {
            'from': alice, 
        }
    )

    aposition_id = dahlia_bank.nextPositionId()-1

    print(mcusd.balanceOf(bob)/ 10 ** 16)
    print(mceur.balanceOf(bob)/ 10 ** 16)

     # open a position
    dahlia_bank.execute(
        0,
        ubeswap_msr_spell,
        ubeswap_msr_spell.addLiquidityWStakingRewards.encode_input(
            mcusd,
            mceur,
            [
             10**15,
             10**15,
             0,
             10**12,
             10**12,
             0,
             0,
             0
            ],
            mcusd_mceur_wmstaking
        ),
        {
            'from': bob, 
        }
    )

    bposition_id = dahlia_bank.nextPositionId()-1

    prevBorrow = dahlia_bank.getBorrowCELOValue(aposition_id)
    time.sleep(30)
    dahlia_bank.accrue(mcusd, {'from': alice})
    dahlia_bank.accrue(mceur, {'from': alice})
    postBorrow = dahlia_bank.getBorrowCELOValue(aposition_id)

    print(prevBorrow / 10 ** 18)
    print(postBorrow / 10 ** 18)

    curABal = mcusd.balanceOf(alice)
    curBBal = mceur.balanceOf(alice)

    print('alice delta A Bal', curABal - prevABal)
    print('alice delta B Bal', curBBal - prevBBal)

    prevABal = mcusd.balanceOf(alice)
    prevBBal = mceur.balanceOf(alice)

    dahlia_bank.execute(
        bposition_id,
        ubeswap_msr_spell,
        ubeswap_msr_spell.removeLiquidityWStakingRewards.encode_input(
            mcusd,
            mceur,
            [2**256-1,
             0,
             2**256-1,
             2**256-1,
             0,
             0,
             0],
            mcusd_mceur_wmstaking
        ),
        {'from': bob}
    )

    time.sleep(15)

    # close the position
    dahlia_bank.execute(
        aposition_id,
        ubeswap_msr_spell,
        ubeswap_msr_spell.removeLiquidityWStakingRewards.encode_input(
            mcusd,
            mceur,
            [2**256-1,
             0,
             2**256-1,
             2**256-1,
             0,
             0,
             0],
            mcusd_mceur_wmstaking
        ),
        {'from': alice}
    )

    a_post_ube = ube.balanceOf(alice)

    curABal = mcusd.balanceOf(alice)
    curBBal = mceur.balanceOf(alice)

    finalABal = curABal
    finalBBal = curBBal

    tokenAPrice = core_oracle.getCELOPx(mcusd)
    tokenBPrice = core_oracle.getCELOPx(mceur)

    print('alice delta A Bal', curABal - prevABal)
    print('alice delta B Bal', curBBal - prevBBal)

    # print('token A price', tokenAPrice)
    # print('token B price', tokenBPrice)

    assert almostEqual(tokenAPrice * initABal + tokenBPrice * initBBal,
                       tokenAPrice * finalABal + tokenBPrice * finalBBal), 'too much value lost'

    assert a_post_ube > a_prev_ube

    a_post_ube = ube.balanceOf(alice)
    a_post_moo = moo.balanceOf(alice)
    b_post_ube = ube.balanceOf(bob)
    b_post_moo = moo.balanceOf(bob)

    print('alice ube', a_post_ube-a_prev_ube)
    print('alice moo', a_post_moo-a_prev_moo)
    print('bob ube', b_post_ube-b_prev_ube)
    print('bob moo', b_post_moo-b_prev_moo)
