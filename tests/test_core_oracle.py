import pytest
from brownie import interface
import brownie
from brownie.exceptions import VirtualMachineError


def test_governor(admin, core_oracle):
    assert core_oracle.governor() == admin


def test_pending_governor(core_oracle):
    assert core_oracle.pendingGovernor() == '0x0000000000000000000000000000000000000000'


def test_set_governor(admin, alice, core_oracle):
    assert core_oracle.governor() == admin
    assert core_oracle.pendingGovernor() == '0x0000000000000000000000000000000000000000'
    # set pending governor to alice
    core_oracle.setPendingGovernor(alice, {'from': admin})
    assert core_oracle.governor() == admin
    assert core_oracle.pendingGovernor() == alice
    # accept governor
    core_oracle.acceptGovernor({'from': alice})
    assert core_oracle.governor() == alice
    assert core_oracle.pendingGovernor() == '0x0000000000000000000000000000000000000000'


def test_not_governor(admin, alice, bob, eve, core_oracle):
    assert core_oracle.governor() == admin
    assert core_oracle.pendingGovernor() == '0x0000000000000000000000000000000000000000'
    # not governor tries to set governor
    with brownie.reverts('not the governor'):
        core_oracle.setPendingGovernor(bob, {'from': alice})
    assert core_oracle.governor() == admin
    assert core_oracle.pendingGovernor() == '0x0000000000000000000000000000000000000000'
    # admin sets self
    core_oracle.setPendingGovernor(admin, {'from': admin})
    assert core_oracle.governor() == admin
    assert core_oracle.pendingGovernor() == admin
    # accept self
    core_oracle.acceptGovernor({'from': admin})
    assert core_oracle.governor() == admin
    assert core_oracle.pendingGovernor() == '0x0000000000000000000000000000000000000000'
    # governor sets another
    core_oracle.setPendingGovernor(alice, {'from': admin})
    assert core_oracle.governor() == admin
    assert core_oracle.pendingGovernor() == alice
    # alice tries to set without accepting
    with brownie.reverts('not the governor'):
        core_oracle.setPendingGovernor(admin, {'from': alice})
    assert core_oracle.governor() == admin
    assert core_oracle.pendingGovernor() == alice
    # eve tries to accept
    with brownie.reverts('not the pending governor'):
        core_oracle.acceptGovernor({'from': eve})
    assert core_oracle.governor() == admin
    assert core_oracle.pendingGovernor() == alice
    # alice accepts governor
    core_oracle.acceptGovernor({'from': alice})
    assert core_oracle.governor() == alice
    assert core_oracle.pendingGovernor() == '0x0000000000000000000000000000000000000000'


def test_governor_set_twice(admin, alice, eve, core_oracle):
    assert core_oracle.governor() == admin
    assert core_oracle.pendingGovernor() == '0x0000000000000000000000000000000000000000'
    # mistakenly set eve to governor
    core_oracle.setPendingGovernor(eve, {'from': admin})
    assert core_oracle.governor() == admin
    assert core_oracle.pendingGovernor() == eve
    # set another governor before eve can accept
    core_oracle.setPendingGovernor(alice, {'from': admin})
    assert core_oracle.governor() == admin
    assert core_oracle.pendingGovernor() == alice
    # eve can no longer accept governor
    with brownie.reverts('not the pending governor'):
        core_oracle.acceptGovernor({'from': eve})
    # alice accepts governor
    core_oracle.acceptGovernor({'from': alice})
    assert core_oracle.governor() == alice
    assert core_oracle.pendingGovernor() == '0x0000000000000000000000000000000000000000'


def test_set_route(admin, core_oracle, celo, cusd, ceur, ube, simple_oracle, UniswapV2Oracle, SimpleOracle):
    assert core_oracle.routes(cusd) == '0x0000000000000000000000000000000000000000'
    assert core_oracle.routes(ceur) == '0x0000000000000000000000000000000000000000'
    assert core_oracle.routes(ube) == '0x0000000000000000000000000000000000000000'

    simple_oracle.setCELOPx([cusd, ceur, ube], [1, 2, 3])

    # test multiple sourcesc
    simple_oracle_1 = SimpleOracle.deploy({'from': admin})

    simple_oracle_1.setCELOPx([cusd, ceur, ube], [4, 5, 6])

    core_oracle.setRoute([cusd, ceur, ube],
                         [simple_oracle, simple_oracle_1, simple_oracle],
                         {'from': admin})

    assert core_oracle.getCELOPx(cusd) == 1
    assert core_oracle.getCELOPx(ceur) == 5
    assert core_oracle.getCELOPx(ube) == 3
    try:
        core_oracle.getCELOPx(celo)
        assert False, 'tx should revert'
    except VirtualMachineError:
        pass

    # re-set prices
    simple_oracle.setCELOPx([cusd, ceur, ube], [7, 8, 9])
    simple_oracle_1.setCELOPx([cusd, ceur, ube], [10, 11, 12])

    assert core_oracle.getCELOPx(cusd) == 7
    assert core_oracle.getCELOPx(ceur) == 11
    assert core_oracle.getCELOPx(ube) == 9

    # re-route
    core_oracle.setRoute([cusd, ceur, ube],
                         [simple_oracle_1, '0x0000000000000000000000000000000000000000', simple_oracle_1])

    assert core_oracle.getCELOPx(cusd) == 10
    assert core_oracle.getCELOPx(ube) == 12

    try:
        core_oracle.getCELOPx(ceur)
        assert False, 'tx should revert'
    except VirtualMachineError:
        pass


def test_set_route_require(admin, core_oracle, simple_oracle, cusd, ube):
    core_oracle.setRoute([], [])

    with brownie.reverts('inconsistent length'):
        core_oracle.setRoute([cusd], [])

    with brownie.reverts('inconsistent length'):
        core_oracle.setRoute([cusd], ['0x0000000000000000000000000000000000000000',
                                     '0x0000000000000000000000000000000000000000'])

    with brownie.reverts('inconsistent length'):
        core_oracle.setRoute([cusd, ube], ['0x0000000000000000000000000000000000000000'])
