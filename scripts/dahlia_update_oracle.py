from brownie import (
    accounts, ERC20KP3ROracle, UniswapV2Oracle, BalancerPairOracle, ProxyOracle, CoreOracle,
    HomoraBank, CurveOracle, UniswapV2SpellV1, WERC20, WLiquidityGauge, WMasterChef,
    WStakingRewards, SushiswapSpellV1, BalancerSpellV1, CurveSpellV1, UbeswapV1Oracle, SafeBox
)
from brownie import interface
from .utils import *

def main():
    deployer = accounts.load('gh')

    ubeswap_oracle_addr = '0xe425a51a129FDeE65bcc2F7b477634E2724c007e'
    celo_addr = '0xf194afdf50b03e69bd7d057c1aa9e10c9954e4c9'
    cusd_addr = '0x874069fa1eb16d44d622f2e0ca25eea172369bc1'
    ube_addr = '0xbe413cdfdad27e71cf533882c760a91ecd02ab27'

    ubeswap_oracle = UbeswapV1Oracle.at(ubeswap_oracle_addr)

    ubeswap_oracle.update(celo_addr, cusd_addr, {'from': deployer})
    ubeswap_oracle.update(celo_addr, ube_addr, {'from': deployer})

    print('Done!')