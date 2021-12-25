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

    sub_addr = addr.get('alpha')

    celo = interface.IERC20Ex(sub_addr.get('celo'))
    mobi = interface.IERC20Ex(sub_addr.get('mobi'))
    ube = interface.IERC20Ex(sub_addr.get('ube'))

    celo_safebox = SafeBox.at(sub_addr['dcelo'])
    mobi_safebox = SafeBox.at(sub_addr['dmobi'])
    ube_safebox = SafeBox.at(sub_addr['dube'])
    
    dahlia_bank = Contract.from_abi("HomoraBank", sub_addr.get('dahlia_bank'), HomoraBank.abi)
    ufactory = interface.IUniswapV2Factory(sub_addr.get('ube_factory'))
    ubeswap_msr_spell = UniswapV2SpellV1.at(sub_addr['ubeswap_spell'])
    core_oracle = CoreOracle.at(sub_addr['core_oracle'])

    celo_mobi_wmstaking = WMStakingRewards.at(sub_addr.get('celo_mobi_wmstaking'))
    celo_ube_wmstaking = WMStakingRewards.at(sub_addr.get('celo_ube_wmstaking'))

    a_prev_ube = ube.balanceOf(alice)
    a_prev_mobi = mobi.balanceOf(alice)
    b_prev_ube = ube.balanceOf(bob)
    b_prev_mobi = mobi.balanceOf(bob)

    prevABal = celo.balanceOf(alice)
    prevBBal = mobi.balanceOf(alice)

    initABal = prevABal
    initBBal = prevBBal

    celo.approve(dahlia_bank, 2**256-1, {'from': alice})
    # mobi.approve(dahlia_bank, 2**256-1, {'from': alice})

    celo.approve(dahlia_bank, 2**256-1, {'from': bob})
    # mobi.approve(dahlia_bank, 2**256-1, {'from': bob})

    print(prevABal, prevBBal)

    # open a position
    dahlia_bank.execute(
        0,
        ubeswap_msr_spell,
        ubeswap_msr_spell.addLiquidityWStakingRewards.encode_input(
            celo,
            mobi,
            [
             40 * 10**14,
             10**14,
             0,
             40 * 10**11,
             10**11,
             0,
             0,
             0
            ],
            celo_mobi_wmstaking
        ),
        {
            'from': alice, 
        }
    )

    aposition_id = dahlia_bank.nextPositionId()-1

    print(celo.balanceOf(bob)/ 10 ** 14)
    print(mobi.balanceOf(bob)/ 10 ** 14)

     # open a position
    dahlia_bank.execute(
        0,
        ubeswap_msr_spell,
        ubeswap_msr_spell.addLiquidityWStakingRewards.encode_input(
            celo,
            mobi,
            [
             40 * 10**13,
             10**13,
             0,
             40 * 10**10,
             10**10,
             0,
             0,
             0
            ],
            celo_mobi_wmstaking
        ),
        {
            'from': bob, 
        }
    )

    bposition_id = dahlia_bank.nextPositionId()-1

    prevBorrow = dahlia_bank.getBorrowCELOValue(aposition_id)
    time.sleep(30)
    dahlia_bank.accrue(celo, {'from': alice})
    dahlia_bank.accrue(mobi, {'from': alice})
    postBorrow = dahlia_bank.getBorrowCELOValue(aposition_id)

    print(prevBorrow / 10 ** 18)
    print(postBorrow / 10 ** 18)

    curABal = celo.balanceOf(alice)
    curBBal = mobi.balanceOf(alice)

    print('alice delta A Bal', curABal - prevABal)
    print('alice delta B Bal', curBBal - prevBBal)

    prevABal = celo.balanceOf(alice)
    prevBBal = mobi.balanceOf(alice)

    dahlia_bank.execute(
        bposition_id,
        ubeswap_msr_spell,
        ubeswap_msr_spell.removeLiquidityWStakingRewards.encode_input(
            celo,
            mobi,
            [2**256-1,
             0,
             2**256-1,
             2**256-1,
             0,
             0,
             0],
            celo_mobi_wmstaking
        ),
        {'from': bob}
    )

    time.sleep(15)

    # close the position
    dahlia_bank.execute(
        aposition_id,
        ubeswap_msr_spell,
        ubeswap_msr_spell.removeLiquidityWStakingRewards.encode_input(
            celo,
            mobi,
            [2**256-1,
             0,
             2**256-1,
             2**256-1,
             0,
             0,
             0],
            celo_mobi_wmstaking
        ),
        {'from': alice}
    )

    a_post_ube = ube.balanceOf(alice)

    curABal = celo.balanceOf(alice)
    curBBal = mobi.balanceOf(alice)

    finalABal = curABal
    finalBBal = curBBal

    tokenAPrice = core_oracle.getCELOPx(celo)
    tokenBPrice = core_oracle.getCELOPx(mobi)

    print('alice delta A Bal', curABal - prevABal)
    print('alice delta B Bal', curBBal - prevBBal)

    print("pre balance", tokenAPrice * initABal + tokenBPrice * initBBal)
    print("post balance", tokenAPrice * finalABal + tokenBPrice * finalBBal)

    assert a_post_ube > a_prev_ube

    a_post_ube = ube.balanceOf(alice)
    a_post_mobi = mobi.balanceOf(alice)
    b_post_ube = ube.balanceOf(bob)
    b_post_mobi = mobi.balanceOf(bob)

    print('alice ube', a_post_ube-a_prev_ube)
    print('alice mobi', a_post_mobi-a_prev_mobi)
    print('bob ube', b_post_ube-b_prev_ube)
    print('bob mobi', b_post_mobi-b_prev_mobi)
