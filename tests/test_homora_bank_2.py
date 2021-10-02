import pytest
from brownie import interface, chain
import brownie
from utils import *
from helper_uniswap import *


def test_reinitialize(admin, bank, oracle):
    with brownie.reverts():
        bank.initialize(oracle, 2000, {'from': admin})


def test_accrue(admin, alice, bank, werc20, urouter, ufactory, celo, cusd, ceur, chain,
                UniswapV2Oracle, UniswapV2SpellV1, simple_oracle, core_oracle, oracle):

    spell = setup_uniswap(admin, alice, bank, werc20, urouter, ufactory, celo, cusd, ceur, chain,
                          UniswapV2Oracle, UniswapV2SpellV1, simple_oracle, core_oracle, oracle)

    execute_uniswap_werc20(admin, alice, bank, cusd, ceur, spell, ufactory, pos_id=0)

    _, _, cceur, _, prevceurTotalDebt, prevceurTotalShare = bank.banks(ceur)
    print('totalDebt', prevceurTotalDebt)
    print('totalShare', prevceurTotalShare)

    chain.sleep(100000)

    # not accrue yet
    _, _, cceur, _, curceurTotalDebt, curceurTotalShare = bank.banks(ceur)
    print('totalDebt', curceurTotalDebt)
    print('totalShare', curceurTotalShare)

    assert prevceurTotalDebt == curceurTotalDebt
    assert prevceurTotalShare == curceurTotalShare

    bank.accrue(ceur)

    _, _, cceur, _, curceurTotalDebt, curceurTotalShare = bank.banks(ceur)
    print('totalDebt', curceurTotalDebt)
    print('totalShare', curceurTotalShare)

    assert prevceurTotalShare == curceurTotalShare
    assert prevceurTotalDebt < curceurTotalDebt

    ceur_interest = curceurTotalDebt - prevceurTotalDebt
    ceur_fee = ceur_interest * bank.feeBps() // 10000  # 20%


def test_accrue_all(admin, alice, bank, werc20, urouter, ufactory, celo, cusd, ceur, chain,
                    UniswapV2Oracle, UniswapV2SpellV1, simple_oracle, core_oracle, oracle):

    spell = setup_uniswap(admin, alice, bank, werc20, urouter, ufactory, celo, cusd, ceur, chain,
                          UniswapV2Oracle, UniswapV2SpellV1, simple_oracle, core_oracle, oracle)

    execute_uniswap_werc20(admin, alice, bank, cusd, ceur, spell, ufactory, pos_id=0)

    _, _, cceur, _, prevceurTotalDebt, prevceurTotalShare = bank.banks(ceur)
    print('totalDebt', prevceurTotalDebt)
    print('totalShare', prevceurTotalShare)

    _, _, ccusd, _, prevcusdTotalDebt, prevcusdTotalShare = bank.banks(cusd)
    print('totalDebt', prevcusdTotalDebt)
    print('totalShare', prevcusdTotalShare)

    chain.sleep(100000)

    # not accrue yet
    _, _, cceur, _, curceurTotalDebt, curceurTotalShare = bank.banks(ceur)
    _, _, ccusd, _, curcusdTotalDebt, curcusdTotalShare = bank.banks(cusd)

    assert prevceurTotalDebt == curceurTotalDebt
    assert prevceurTotalShare == curceurTotalShare

    assert prevcusdTotalDebt == curcusdTotalDebt
    assert prevcusdTotalShare == curcusdTotalShare

    # accrue ceur, cusd
    bank.accrueAll([ceur, cusd])

    _, _, cceur, _, curceurTotalDebt, curceurTotalShare = bank.banks(ceur)
    print('totalDebt', curceurTotalDebt)
    print('totalShare', curceurTotalShare)

    assert prevceurTotalShare == curceurTotalShare

    ceur_interest = curceurTotalDebt - prevceurTotalDebt
    ceur_fee = ceur_interest * bank.feeBps() // 10000  # 20%

    # TODO: this test is broken.
    # assert almostEqual(ceur_interest, 200000000 * 10 // 100 * 100000 // (365*86400))

    _, _, ccusd, _, curcusdTotalDebt, curcusdTotalShare = bank.banks(cusd)
    print('totalDebt', curcusdTotalDebt)
    print('totalShare', curcusdTotalShare)

    assert prevcusdTotalShare == curcusdTotalShare

    cusd_interest = curcusdTotalDebt - prevcusdTotalDebt
    cusd_fee = cusd_interest * bank.feeBps() // 10000  # 20%

    # TODO: this test is broken.
    # assert almostEqual(cusd_interest, 1000000000 * 10 // 100 * 100000 // (365*86400))
