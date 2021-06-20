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
    cycelo_addr = '0x5e3A00F9DaB4b241780Fbc11529Db14e1C8D2f1D'
    cycusd_addr = '0x136dE673A9d27301aBa3390B5CFF4d56Bc11d799'
    cyube_addr = ''
    dahlia_bank_addr = '0x05c9E9fBE4093f3F2f88328F559f82FF606238fD'

    celo = interface.IERC20Ex(celo_addr)
    cusd = interface.IERC20Ex(cusd_addr)
    ube = interface.IERC20Ex(ube_addr)
    cycelo = interface.IERC20Ex.at(cycelo_addr)
    cycusd = interface.IERC20Ex.at(cycusd_addr)
    cyube = interface.IERC20Ex.at(cyube_addr)
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
