from brownie import (
    accounts, ERC20KP3ROracle, UniswapV2Oracle, BalancerPairOracle, ProxyOracle, CoreOracle,
    HomoraBank, CurveOracle, UniswapV2SpellV1, WERC20, WLiquidityGauge, WMasterChef,
    WStakingRewards, SushiswapSpellV1, BalancerSpellV1, CurveSpellV1, UbeswapV1Oracle, SafeBox
)
from brownie import interface
from .utils import *

def main():
    # deployer = accounts.at('0xB593d82d53e2c187dc49673709a6E9f806cdC835', force=True)
    deployer = accounts.load('gh')

    celo_addr = '0xf194afdf50b03e69bd7d057c1aa9e10c9954e4c9'
    cusd_addr = '0x874069fa1eb16d44d622f2e0ca25eea172369bc1'
    ube_addr = '0xbe413cdfdad27e71cf533882c760a91ecd02ab27'
    cycelo_addr = '0x9Ce844b3A315FE2CBB22b88B3Eb0921dD7a2e018'
    cycusd_addr = '0xE5283EAE77252275e6207AC25AAF7A0A4004EEFe'
    cyube_addr = '0x6850Ee9921fD9FF2419a59Cf7417B0e18EE0A4Bc'
    dahlia_bank_addr = '0x0460878568C92D877f5544a2F3a1523E6c2bB1CA'

    celo = interface.IERC20Ex(celo_addr)
    cusd = interface.IERC20Ex(cusd_addr)
    ube = interface.IERC20Ex(ube_addr)
    cycelo = interface.IERC20Ex(cycelo_addr)
    cycusd = interface.IERC20Ex(cycusd_addr)
    cyube = interface.IERC20Ex(cyube_addr)
    dahlia_bank = HomoraBank.at(dahlia_bank_addr)

    dahlia_bank.setWhitelistTokens([celo, cusd, ube], [True, True, True], {'from': deployer})

    # deploy safeboxes

    safebox_celo = SafeBox.deploy(
        cycelo, 'Interest Bearing Celo', 'dCELO', {'from': deployer})
    safebox_cusd = SafeBox.deploy(
        cycusd, 'Interest Bearing Celo US Dollar', 'dcUSD', {'from': deployer})
    safebox_ube = SafeBox.deploy(
        cyube, 'Interest Bearing UBE', 'dUBE', {'from': deployer})

    # add banks
    dahlia_bank.addBank(celo, cycelo, {'from': deployer})
    dahlia_bank.addBank(cusd, cycusd, {'from': deployer})
    dahlia_bank.addBank(ube, cyube, {'from': deployer})

    print('Done!')
