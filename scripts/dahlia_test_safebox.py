from brownie import (
    SafeBox,
    accounts,
    interface,
    network,
)
import json


def almostEqual(a, b):
    thresh = 0.01
    return a <= b + thresh * abs(b) and a >= b - thresh * abs(b)

network.gas_limit(8000000)

def main():
    alice = accounts.load('dahlia_alice')
    bob = accounts.load('dahlia_bob')
    f = open('scripts/dahlia_addresses.json')
    addr = json.load(f)['mainnet']

    cusd = interface.IERC20Ex(addr['cusd'])
    fcusd = interface.IERC20Ex(addr['fcusd'])
    cusd_safebox = SafeBox.at(addr['dcusd'])

    cusd.approve(cusd_safebox, 2**256-1, {'from': alice})
    cusd.approve(cusd_safebox, 2**256-1, {'from': bob})

    #################################################################
    # deposit
    print('====================================')
    print('Case 1. deposit')

    prevDAIAlice = cusd.balanceOf(alice)
    prevDAIBob = cusd.balanceOf(bob)
    prevIBDAIAlice = cusd_safebox.balanceOf(alice)
    prevIBDAIBob = cusd_safebox.balanceOf(bob)

    alice_amt = 10**16
    bob_amt = 10**16
    cusd_safebox.deposit(alice_amt, {'from': alice})
    cusd_safebox.deposit(bob_amt, {'from': bob})

    curDAIAlice = cusd.balanceOf(alice)
    curDAIBob = cusd.balanceOf(bob)
    curIBDAIAlice = cusd_safebox.balanceOf(alice)
    curIBDAIBob = cusd_safebox.balanceOf(bob)

    print('∆ dai alice', curDAIAlice - prevDAIAlice)
    print('∆ dai bob', curDAIBob - prevDAIBob)
    print('∆ ibDAI bal alice', curIBDAIAlice - prevIBDAIAlice)
    print('∆ ibDAI bal bob', curIBDAIBob - prevIBDAIBob)
    print('calculated ibDAI alice', alice_amt * 10**18 // fcusd.exchangeRateStored())
    print('calculated ibDAI bob', bob_amt * 10**18 // fcusd.exchangeRateStored())

    assert curDAIAlice - prevDAIAlice == -alice_amt, 'incorrect alice amount'
    assert curDAIBob - prevDAIBob == -bob_amt, 'incorrect bob amount'
    assert almostEqual(curIBDAIAlice - prevIBDAIAlice,
                       alice_amt * 10**18 // fcusd.exchangeRateStored())
    assert almostEqual(curIBDAIBob - prevIBDAIBob,
                       bob_amt * 10**18 // fcusd.exchangeRateStored())


    #################################################################
    # alice withdraws 1/3 & 2/3. bob withdraws all.
    print('====================================')
    print('Case 2. withdraw')

    alice_withdraw_1 = alice_amt // 3
    alice_withdraw_2 = alice_amt - alice_withdraw_1
    bob_withdraw = bob_amt
    prevDAIAlice = cusd.balanceOf(alice)
    prevDAIBob = cusd.balanceOf(bob)
    prevIBDAIAlice = cusd_safebox.balanceOf(alice)
    prevIBDAIBob = cusd_safebox.balanceOf(bob)

    cusd_safebox.withdraw(alice_withdraw_1, {'from': alice})
    cusd_safebox.withdraw(bob_withdraw, {'from': bob})

    curDAIAlice = cusd.balanceOf(alice)
    curDAIBob = cusd.balanceOf(bob)
    curIBDAIAlice = cusd_safebox.balanceOf(alice)
    curIBDAIBob = cusd_safebox.balanceOf(bob)

    print('∆ dai alice', curDAIAlice - prevDAIAlice)
    print('∆ dai bob', curDAIBob - prevDAIBob)
    print('∆ ibDAI bal alice', curIBDAIAlice - prevIBDAIAlice)
    print('∆ ibDAI bal bob', curIBDAIBob - prevIBDAIBob)
    print(alice_withdraw_1)

    assert almostEqual(curDAIAlice - prevDAIAlice, alice_amt //
                       3), 'incorrect alice withdraw dai amount'
    assert almostEqual(curDAIBob - prevDAIBob, bob_amt), 'incorrect bob withdraw dai amount'
    assert curIBDAIAlice - prevIBDAIAlice == -alice_withdraw_1, 'incorrect alice ∆ibDAI'
    assert curIBDAIBob - prevIBDAIBob == -bob_withdraw, 'incorrect bob ∆ibDAI'

    prevDAIAlice = cusd.balanceOf(alice)
    prevIBDAIAlice = cusd_safebox.balanceOf(alice)

    cusd_safebox.withdraw(alice_withdraw_2, {'from': alice})

    curDAIAlice = cusd.balanceOf(alice)
    curIBDAIAlice = cusd_safebox.balanceOf(alice)

    print('∆ dai alice', curDAIAlice - prevDAIAlice)
    print('∆ dai bob', curDAIBob - prevDAIBob)
    print('∆ ibDAI bal alice', curIBDAIAlice - prevIBDAIAlice)
    print('∆ ibDAI bal bob', curIBDAIBob - prevIBDAIBob)

    assert almostEqual(curDAIAlice - prevDAIAlice, alice_amt * 2 //
                       3), 'incorrect alice second withdraw dai amount'
    assert curIBDAIAlice - prevIBDAIAlice == -alice_withdraw_2, 'incorrect alice second ∆ibDAI '

    cusd.approve(cusd_safebox, 0, {'from': alice})
    cusd.approve(cusd_safebox, 0, {'from': bob})

    print('Done!')
