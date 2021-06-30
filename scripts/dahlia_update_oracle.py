from brownie import (
    accounts, ERC20KP3ROracle, UniswapV2Oracle, BalancerPairOracle, ProxyOracle, CoreOracle,
    HomoraBank, CurveOracle, UniswapV2SpellV1, WERC20, WLiquidityGauge, WMasterChef,
    WStakingRewards, SushiswapSpellV1, BalancerSpellV1, CurveSpellV1, UbeswapV1Oracle, SafeBox
)
from brownie import interface
from .utils import *
import json

def main():
    deployer = accounts.load('gh')
    f = open('scripts/dahlia_addresses.json')
    addr = json.load(f)['alfajores']

    ubeswap_oracle = UbeswapV1Oracle.at(addr['ube_oracle'])

    ubeswap_oracle.update(addr['celo'], addr['cusd'], {'from': deployer})
    ubeswap_oracle.update(addr['celo'], addr['ube'], {'from': deployer})

    print('Done!')