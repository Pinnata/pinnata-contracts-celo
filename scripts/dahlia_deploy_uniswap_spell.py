from brownie import (
    accounts, ERC20KP3ROracle, UniswapV2Oracle, BalancerPairOracle, ProxyOracle, CoreOracle,
    HomoraBank, CurveOracle, UniswapV2SpellV1, WERC20, WLiquidityGauge, WMasterChef,
    WStakingRewards, SushiswapSpellV1, BalancerSpellV1, CurveSpellV1, UbeswapV1Oracle, SafeBox
)
from brownie import interface
from .utils import *

def main():
    deployer = accounts.load('gh')

    celo_addr = '0xf194afdf50b03e69bd7d057c1aa9e10c9954e4c9'
    cusd_addr = '0x874069fa1eb16d44d622f2e0ca25eea172369bc1'
    ube_addr = '0xbe413cdfdad27e71cf533882c760a91ecd02ab27'
    ube_router_addr = '0xE3D8bd6Aed4F159bc8000a9cD47CffDb95F96121'
    werc20_addr = '0x38E04E9c49844aF8123da9475576cdD1195e0916'
    dahlia_bank_addr = '0x0460878568C92D877f5544a2F3a1523E6c2bB1CA'

    celo = interface.IERC20Ex(celo_addr)
    cusd = interface.IERC20Ex(cusd_addr)
    ube = interface.IERC20Ex(ube_addr)
    ube_router = interface.IUniswapV2Router02(ube_router_addr)
    werc20 = WERC20.at(werc20_addr)
    dahlia_bank = HomoraBank.at(dahlia_bank_addr)

    uniswap_spell = UniswapV2SpellV1.deploy(
        dahlia_bank, werc20, ube_router, celo,
        {'from': deployer},
    )

    uniswap_spell.getAndApprovePair(celo, cusd, {'from': deployer})
    uniswap_spell.getAndApprovePair(celo, ube, {'from': deployer})

    ube_factory_address = ube_router.factory()
    ube_factory = interface.IUniswapV2Factory(ube_factory_address)
    celo_cusd_lp = ube_factory.getPair(celo, cusd)
    celo_ube_lp = ube_factory.getPair(celo, ube)

    uniswap_spell.setWhitelistLPTokens([celo_cusd_lp], [True], {'from': deployer})
    uniswap_spell.setWhitelistLPTokens([celo_ube_lp], [True], {'from': deployer})

    dahlia_bank.setWhitelistSpells([uniswap_spell], [True], {'from': deployer})

    print('Done!')
