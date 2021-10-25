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

    bob_amt = 10**18
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

    celo_mcusd_lp = interface.IERC20Ex(ufactory.getPair(celo, mcusd))
    celo_mceur_lp = interface.IERC20Ex(ufactory.getPair(celo, mceur))
    mcusd_mceur_lp = interface.IERC20Ex(ufactory.getPair(mcusd, mceur))

    a_prev_ube = ube.balanceOf(alice)
    # aPrevMOM = mock2.balanceOf(alice)
    b_prev_ube = ube.balanceOf(bob)
    # bPrevMOM = mock2.balanceOf(bob)

    lend(bob, celo, celo_safebox)
    lend(bob, mcusd, mcusd_safebox)

    prevABal = celo.balanceOf(alice)
    prevBBal = mcusd.balanceOf(alice)

    initABal = prevABal
    initBBal = prevBBal

    celo.approve(dahlia_bank, 2**256-1, {'from': alice})
    mcusd.approve(dahlia_bank, 2**256-1, {'from': alice})

    celo.approve(dahlia_bank, 2**256-1, {'from': bob})
    mcusd.approve(dahlia_bank, 2**256-1, {'from': bob})

    # open a position
    dahlia_bank.execute(
        0,
        ubeswap_msr_spell,
        ubeswap_msr_spell.addLiquidityWStakingRewards.encode_input(
            mcusd,
            celo,
            [
             6*10**16,
             10**16,
             0,
             9*10**14,
             1.5*10**14,
             0,
             0,
             0
            ],
            celo_mcusd_wmstaking
        ),
        {
            'from': alice, 
        }
    )

    aposition_id = dahlia_bank.nextPositionId()-1

     # open a position
    dahlia_bank.execute(
        0,
        ubeswap_msr_spell,
        ubeswap_msr_spell.addLiquidityWStakingRewards.encode_input(
            mcusd,
            celo,
            [
             6*10**15,
             10**15,
             0,
             9*10**13,
             1.5*10**13,
             0,
             0,
             0
            ],
            celo_mcusd_wmstaking
        ),
        {
            'from': bob, 
        }
    )

    bposition_id = dahlia_bank.nextPositionId()-1

    prevBorrow = dahlia_bank.getBorrowCELOValue(aposition_id)
    time.sleep(30)
    dahlia_bank.accrue(mcusd, {'from': alice})
    dahlia_bank.accrue(celo, {'from': alice})
    postBorrow = dahlia_bank.getBorrowCELOValue(aposition_id)

    assert prevBorrow < postBorrow

    curABal = celo.balanceOf(alice)
    curBBal = mcusd.balanceOf(alice)

    print('alice delta A Bal', curABal - prevABal)
    print('alice delta B Bal', curBBal - prevBBal)

    prevABal = celo.balanceOf(alice)
    prevBBal = mcusd.balanceOf(alice)

    dahlia_bank.execute(
        bposition_id,
        ubeswap_msr_spell,
        ubeswap_msr_spell.removeLiquidityWStakingRewards.encode_input(
            mcusd,
            celo,
            [2**256-1,
             0,
             2**256-1,
             2**256-1,
             0,
             0,
             0],
            celo_mcusd_wmstaking
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
            celo,
            [2**256-1,
             0,
             2**256-1,
             2**256-1,
             0,
             0,
             0],
            celo_mcusd_wmstaking
        ),
        {'from': alice}
    )

    a_post_ube = ube.balanceOf(alice)
    # aPostMOM = mock2.balanceOf(alice)

    curABal = celo.balanceOf(alice)
    # curBBal = cusd.balanceOf(alice)

    finalABal = curABal
    finalBBal = curBBal

    tokenAPrice = core_oracle.getCELOPx(celo)
    tokenBPrice = core_oracle.getCELOPx(mcusd)

    print('alice delta A Bal', curABal - prevABal)
    print('alice delta B Bal', curBBal - prevBBal)

    # print('token A price', tokenAPrice)
    # print('token B price', tokenBPrice)

    assert almostEqual(tokenAPrice * initABal + tokenBPrice * initBBal,
                       tokenAPrice * finalABal + tokenBPrice * finalBBal), 'too much value lost'

    assert a_post_ube > a_prev_ube

    a_post_ube = ube.balanceOf(alice)
    # aPostMOM = mock2.balanceOf(alice)
    b_post_ube = ube.balanceOf(bob)
    # bPostMOM = mock2.balanceOf(bob)

    print('alice grow', a_post_ube-a_prev_ube)
    # print('alice mom', aPostMOM-aPrevMOM)
    print('bob grow', b_post_ube-b_prev_ube)
    # print('bob mom', bPostMOM-bPrevMOM)
