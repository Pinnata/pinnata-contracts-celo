from brownie import (SafeBox, HomoraBank)
from brownie import accounts, interface, chain
from .utils import *


def almostEqual(a, b):
    thresh = 0.01
    return a <= b + thresh * abs(b) and a >= b - thresh * abs(b)


def main():
    alice = accounts.load('alice')
    bob = accounts.load('bob')

    cusd_addr = '0x874069fa1eb16d44d622f2e0ca25eea172369bc1'
    cycusd_addr = '0xE5283EAE77252275e6207AC25AAF7A0A4004EEFe'
    cusd_safebox_addr = '0x2FF09993ebA7292fb93d3F2F87ec498B5c361c64'

    cusd = interface.IERC20Ex(cusd_addr)
    cycusd = interface.IERC20Ex(cycusd_addr)
    cusd_safebox = SafeBox.at(cusd_safebox_addr)

    # approve dai
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

    alice_amt = 10**18
    bob_amt = 10**18
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
    print('calculated ibDAI alice', alice_amt * 10**18 // cycusd.exchangeRateStored())
    print('calculated ibDAI bob', bob_amt * 10**18 // cycusd.exchangeRateStored())

    assert curDAIAlice - prevDAIAlice == -alice_amt, 'incorrect alice amount'
    assert curDAIBob - prevDAIBob == -bob_amt, 'incorrect bob amount'
    assert almostEqual(curIBDAIAlice - prevIBDAIAlice,
                       alice_amt * 10**18 // cycusd.exchangeRateStored())
    assert almostEqual(curIBDAIBob - prevIBDAIBob,
                       bob_amt * 10**18 // cycusd.exchangeRateStored())


    #################################################################
    # alice withdraws 1/3 & 2/3. bob withdraws all.
    print('====================================')
    print('Case 2. withdraw')

    alice_withdraw_1 = cusd_safebox.balanceOf(alice) // 3
    alice_withdraw_2 = cusd_safebox.balanceOf(alice) - alice_withdraw_1
    bob_withdraw = cusd_safebox.balanceOf(bob)

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

    print('Done!')
