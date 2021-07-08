import pytest
import brownie
from brownie import interface


def test_governor(admin, safebox):
    assert safebox.governor() == admin


def test_pending_governor(safebox):
    assert safebox.pendingGovernor() == '0x0000000000000000000000000000000000000000'


def test_set_governor(admin, alice, safebox):
    assert safebox.governor() == admin
    assert safebox.pendingGovernor() == '0x0000000000000000000000000000000000000000'
    # set pending governor to alice
    safebox.setPendingGovernor(alice, {'from': admin})
    assert safebox.governor() == admin
    assert safebox.pendingGovernor() == alice
    # accept governor
    safebox.acceptGovernor({'from': alice})
    assert safebox.governor() == alice
    assert safebox.pendingGovernor() == '0x0000000000000000000000000000000000000000'


def test_not_governor(admin, alice, bob, eve, safebox):
    assert safebox.governor() == admin
    assert safebox.pendingGovernor() == '0x0000000000000000000000000000000000000000'
    # not governor tries to set governor
    with brownie.reverts('not the governor'):
        safebox.setPendingGovernor(bob, {'from': alice})
    assert safebox.governor() == admin
    assert safebox.pendingGovernor() == '0x0000000000000000000000000000000000000000'
    # admin sets self
    safebox.setPendingGovernor(admin, {'from': admin})
    assert safebox.governor() == admin
    assert safebox.pendingGovernor() == admin
    # accept self
    safebox.acceptGovernor({'from': admin})
    assert safebox.governor() == admin
    assert safebox.pendingGovernor() == '0x0000000000000000000000000000000000000000'
    # governor sets another
    safebox.setPendingGovernor(alice, {'from': admin})
    assert safebox.governor() == admin
    assert safebox.pendingGovernor() == alice
    # alice tries to set without accepting
    with brownie.reverts('not the governor'):
        safebox.setPendingGovernor(admin, {'from': alice})
    assert safebox.governor() == admin
    assert safebox.pendingGovernor() == alice
    # eve tries to accept
    with brownie.reverts('not the pending governor'):
        safebox.acceptGovernor({'from': eve})
    assert safebox.governor() == admin
    assert safebox.pendingGovernor() == alice
    # alice accepts governor
    safebox.acceptGovernor({'from': alice})
    assert safebox.governor() == alice
    assert safebox.pendingGovernor() == '0x0000000000000000000000000000000000000000'


def test_governor_set_twice(admin, alice, eve, safebox):
    assert safebox.governor() == admin
    assert safebox.pendingGovernor() == '0x0000000000000000000000000000000000000000'
    # mistakenly set eve to governor
    safebox.setPendingGovernor(eve, {'from': admin})
    assert safebox.governor() == admin
    assert safebox.pendingGovernor() == eve
    # set another governor before eve can accept
    safebox.setPendingGovernor(alice, {'from': admin})
    assert safebox.governor() == admin
    assert safebox.pendingGovernor() == alice
    # eve can no longer accept governor
    with brownie.reverts('not the pending governor'):
        safebox.acceptGovernor({'from': eve})
    # alice accepts governor
    safebox.acceptGovernor({'from': alice})
    assert safebox.governor() == alice
    assert safebox.pendingGovernor() == '0x0000000000000000000000000000000000000000'


def test_deposit_withdraw(admin, alice, token, cToken, safebox):
    alice_mint_amt = 1000 * 10**18
    token.mint(alice, alice_mint_amt, {'from': admin})
    token.approve(safebox, 2**256-1, {'from': alice})

    alice_deposit_amt = 10 * 10**18
    safebox.deposit(alice_deposit_amt, {'from': alice})
    assert token.balanceOf(alice) == alice_mint_amt - alice_deposit_amt
    assert cToken.balanceOf(safebox) == alice_deposit_amt

    print(safebox.balanceOf(alice))

    alice_withdraw_amt = 2 * 10**18
    safebox.withdraw(alice_withdraw_amt, {'from': alice})
    assert token.balanceOf(alice) == alice_mint_amt - alice_deposit_amt + alice_withdraw_amt
    assert cToken.balanceOf(safebox) == alice_deposit_amt - alice_withdraw_amt

    cToken.setMintRate(11 * 10**17)
    assert cToken.mintRate() == 11 * 10**17

    alice_rewithdraw_amt = 3 * 10**18
    safebox.withdraw(alice_rewithdraw_amt, {'from': alice})
    assert token.balanceOf(alice) == alice_mint_amt - alice_deposit_amt + \
        alice_withdraw_amt + alice_rewithdraw_amt * 10 // 11
    assert cToken.balanceOf(safebox) == alice_deposit_amt - \
        alice_withdraw_amt - alice_rewithdraw_amt


