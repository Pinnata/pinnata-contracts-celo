from brownie import (SafeBox, HomoraBank)
from brownie import accounts, interface, chain
from .utils import *
import json


def almostEqual(a, b):
    thresh = 0.01
    return a <= b + thresh * abs(b) and a >= b - thresh * abs(b)


def main():
    alice = accounts.load('alice')
    bob = accounts.load('bob')
    f = open('scripts/dahlia_addresses.json')
    addr = json.load(f)['mainnet']

    ube = interface.IERC20Ex(addr['ube'])
    cyube = interface.IERC20Ex(addr['cyube'])
    ube_safebox = SafeBox.at(addr['ube_safebox'])

    # approve dai
    ube.approve(ube_safebox, 2**256-1, {'from': alice})
    ube.approve(ube_safebox, 2**256-1, {'from': bob})

    #################################################################
    # deposit
    print('====================================')
    print('Case 1. deposit')

    prevDAIAlice = ube.balanceOf(alice)
    prevDAIBob = ube.balanceOf(bob)
    prevIBDAIAlice = ube_safebox.balanceOf(alice)
    prevIBDAIBob = ube_safebox.balanceOf(bob)

    alice_amt = 10**18
    bob_amt = 10**18
    ube_safebox.deposit(alice_amt, {'from': alice})
    ube_safebox.deposit(bob_amt, {'from': bob})

    curDAIAlice = ube.balanceOf(alice)
    curDAIBob = ube.balanceOf(bob)
    curIBDAIAlice = ube_safebox.balanceOf(alice)
    curIBDAIBob = ube_safebox.balanceOf(bob)

    print('∆ dai alice', curDAIAlice - prevDAIAlice)
    print('∆ dai bob', curDAIBob - prevDAIBob)
    print('∆ ibDAI bal alice', curIBDAIAlice - prevIBDAIAlice)
    print('∆ ibDAI bal bob', curIBDAIBob - prevIBDAIBob)
    print('calculated ibDAI alice', alice_amt * 10**18 // cyube.exchangeRateStored())
    print('calculated ibDAI bob', bob_amt * 10**18 // cyube.exchangeRateStored())

    assert curDAIAlice - prevDAIAlice == -alice_amt, 'incorrect alice amount'
    assert curDAIBob - prevDAIBob == -bob_amt, 'incorrect bob amount'
    assert almostEqual(curIBDAIAlice - prevIBDAIAlice,
                       alice_amt * 10**18 // cyube.exchangeRateStored())
    assert almostEqual(curIBDAIBob - prevIBDAIBob,
                       bob_amt * 10**18 // cyube.exchangeRateStored())


    #################################################################
    # alice withdraws 1/3 & 2/3. bob withdraws all.
    print('====================================')
    print('Case 2. withdraw')

    alice_withdraw_1 = ube_safebox.balanceOf(alice) // 3
    alice_withdraw_2 = ube_safebox.balanceOf(alice) - alice_withdraw_1
    bob_withdraw = ube_safebox.balanceOf(bob)

    prevDAIAlice = ube.balanceOf(alice)
    prevDAIBob = ube.balanceOf(bob)
    prevIBDAIAlice = ube_safebox.balanceOf(alice)
    prevIBDAIBob = ube_safebox.balanceOf(bob)

    ube_safebox.withdraw(alice_withdraw_1, {'from': alice})
    ube_safebox.withdraw(bob_withdraw, {'from': bob})

    curDAIAlice = ube.balanceOf(alice)
    curDAIBob = ube.balanceOf(bob)
    curIBDAIAlice = ube_safebox.balanceOf(alice)
    curIBDAIBob = ube_safebox.balanceOf(bob)

    print('∆ dai alice', curDAIAlice - prevDAIAlice)
    print('∆ dai bob', curDAIBob - prevDAIBob)
    print('∆ ibDAI bal alice', curIBDAIAlice - prevIBDAIAlice)
    print('∆ ibDAI bal bob', curIBDAIBob - prevIBDAIBob)

    assert almostEqual(curDAIAlice - prevDAIAlice, alice_amt //
                       3), 'incorrect alice withdraw dai amount'
    assert almostEqual(curDAIBob - prevDAIBob, bob_amt), 'incorrect bob withdraw dai amount'
    assert curIBDAIAlice - prevIBDAIAlice == -alice_withdraw_1, 'incorrect alice ∆ibDAI'
    assert curIBDAIBob - prevIBDAIBob == -bob_withdraw, 'incorrect bob ∆ibDAI'

    prevDAIAlice = ube.balanceOf(alice)
    prevIBDAIAlice = ube_safebox.balanceOf(alice)

    ube_safebox.withdraw(alice_withdraw_2, {'from': alice})

    curDAIAlice = ube.balanceOf(alice)
    curIBDAIAlice = ube_safebox.balanceOf(alice)

    print('∆ dai alice', curDAIAlice - prevDAIAlice)
    print('∆ dai bob', curDAIBob - prevDAIBob)
    print('∆ ibDAI bal alice', curIBDAIAlice - prevIBDAIAlice)
    print('∆ ibDAI bal bob', curIBDAIBob - prevIBDAIBob)

    assert almostEqual(curDAIAlice - prevDAIAlice, alice_amt * 2 //
                       3), 'incorrect alice second withdraw dai amount'
    assert curIBDAIAlice - prevIBDAIAlice == -alice_withdraw_2, 'incorrect alice second ∆ibDAI '

    ube.approve(ube_safebox, 0, {'from': alice})
    ube.approve(ube_safebox, 0, {'from': bob})

    print('Done!')
