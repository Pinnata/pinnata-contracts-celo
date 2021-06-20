from brownie import (
    accounts, ERC20KP3ROracle, UniswapV2Oracle, BalancerPairOracle, ProxyOracle, CoreOracle,
    HomoraBank, CurveOracle, UniswapV2SpellV1, WERC20, WLiquidityGauge, WMasterChef,
    WStakingRewards, SushiswapSpellV1, BalancerSpellV1, CurveSpellV1, UbeswapV1Oracle, SafeBox
)
from brownie import interface
from .utils import *


def almostEqual(a, b):
    thresh = 0.01
    return a <= b + thresh * abs(b) and a >= b - thresh * abs(b)


def test_safebox(token, safebox):
    alice = accounts[1]

    mint_tokens(token, alice)

    token.approve(safebox, 2**256-1, {'from': alice})

    deposit_amt = 100 * 10**token.decimals()

    prevBal = token.balanceOf(alice)
    safebox.deposit(deposit_amt, {'from': alice})
    curBal = token.balanceOf(alice)

    assert almostEqual(curBal - prevBal, -deposit_amt), 'incorrect deposit amount'

    withdraw_amt = safebox.balanceOf(alice) // 3

    prevBal = token.balanceOf(alice)
    safebox.withdraw(withdraw_amt, {'from': alice})
    curBal = token.balanceOf(alice)

    assert almostEqual(curBal - prevBal, deposit_amt // 3), 'incorrect first withdraw amount'

    withdraw_amt = safebox.balanceOf(alice)

    prevBal = token.balanceOf(alice)
    safebox.withdraw(withdraw_amt, {'from': alice})
    curBal = token.balanceOf(alice)

    assert almostEqual(curBal - prevBal, deposit_amt - deposit_amt //
                       3), 'incorrect second withdraw amount'


def test_bank(token, bank):
    alice = accounts[1]

    uniswap_spell = UniswapV2SpellV1.at('0xc671B7251a789de0835a2fa33c83c8D4afB39092')

    mint_tokens(token, alice)

    token.approve(bank, 2**256-1, {'from': alice})

    celo = interface.IERC20Ex('0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2')

    amt = 10000 * 10**token.decimals()

    borrow_amt = 10 * 10**token.decimals()

    prevTokenAlice = token.balanceOf(alice)

    bank.execute(0, uniswap_spell, uniswap_spell.addLiquidityWERC20.encode_input(
        token, celo, [amt, 0, 0, borrow_amt, 10**18, 0, 0, 0]), {'from': alice})

    curTokenAlice = token.balanceOf(alice)

    assert almostEqual(curTokenAlice - prevTokenAlice, -amt), 'incorrect input amt'


def main():
    # deployer = accounts.at('0xB593d82d53e2c187dc49673709a6E9f806cdC835', force=True)
    deployer = accounts.load('gh')

    celo_addr = '0xf194afdf50b03e69bd7d057c1aa9e10c9954e4c9'
    cusd_addr = '0x874069fa1eb16d44d622f2e0ca25eea172369bc1'
    ceur_addr = '0x10c892A6EC43a53E45D0B916B4b7D383B1b78C0F'
    ube_addr = '0xbe413cdfdad27e71cf533882c760a91ecd02ab27'
    celo_cusd_pair_addr = '0xe952fe9608a20f80f009a43AEB6F422750285638'
    ube_celo_pool_addr = '0xAd2E17dad4aE46C8e797316ad44BEEF21D105624'
    ube_router_addr = '0xE3D8bd6Aed4F159bc8000a9cD47CffDb95F96121'

    #TODO: update addresses once fountain deployed
    cycelo_addr = '0x9Ce844b3A315FE2CBB22b88B3Eb0921dD7a2e018'
    cycusd_addr = '0xE5283EAE77252275e6207AC25AAF7A0A4004EEFe'
    cyceur_addr = '0xEb1944A6deD42d0947371039B2078C76c3A62085'
    homorabank_addr = '0xCD9fe42a21DCC22C4BEB11B2e89750870288Fe51'
    uniswap_spell_addr = "0x5F6a662cAc69fE3A0dD22d971F09d49d5AA6fEA9"

# deploy safeboxes

    celo = interface.IERC20Ex(celo_addr)
    cusd = interface.IERC20Ex(cusd_addr)
    ceur = interface.IERC20Ex(ceur_addr)
    celo_cusd_pair = interface.IERC20Ex(celo_cusd_pair_addr)

    bank = HomoraBank.at(homorabank_addr)

    cycelo = interface.IERC20Ex(cycelo_addr)
    cycusd = interface.IERC20Ex(cycusd_addr)
    cyceur = interface.IERC20Ex(cyceur_addr)

    # safebox_celo = SafeBox.deploy(
    #     cycelo, 'Interest Bearing Celo', 'dCELO', {'from': deployer})
    # safebox_cusd = SafeBox.deploy(
    #     cycusd, 'Interest Bearing Celo US Dollar', 'dcUSD', {'from': deployer})
    # safebox_ceur = SafeBox.deploy(
    #     cyceur, 'Interest Bearing Celo Euro', 'dcEUR', {'from': deployer})

    # # add banks
    # bank.addBank(celo, cycelo_addr, {'from': deployer})
    # bank.addBank(cusd, cycusd_addr, {'from': deployer})
    # bank.addBank(ceur, cyceur_addr, {'from': deployer})

    bank.setWhitelistTokens([celo, cusd, ceur, celo_cusd_pair], [True, True, True, True], {'from': deployer})
    uniswap_spell = UniswapV2SpellV1.at(uniswap_spell_addr)
    uniswap_spell.getAndApprovePair(celo, cusd, {'from': deployer})


    ###########################################################
    # test cyToken

    # for token in [cyusdt, cyusdc, cyyfi]:
    #     assert interface.IERC20Ex(token).symbol() == 'cy' + \
    #         interface.IERC20Ex(interface.IERC20Ex(token).underlying()).symbol()

    ###########################################################
    # test safeboxes

    # cusd = interface.IERC20Ex('0x6B175474E89094C44Da98b954EedeAC495271d0F')
    # usdt = interface.IERC20Ex('0xdAC17F958D2ee523a2206206994597C13D831ec7')
    # usdc = interface.IERC20Ex('0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48')
    # yfi = interface.IERC20Ex('0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e')

    # test_safebox_eth(safebox_eth)
    # test_safebox(cusd, safebox_cusd)
    # test_safebox(usdt, safebox_usdt)
    # test_safebox(usdc, safebox_usdc)
    # test_safebox(yfi, safebox_yfi)

    ###########################################################
    # test banks with uniswap spell
    # print('============ testing banks =============')

    # test_bank(usdt, bank)
    # test_bank(usdc, bank)