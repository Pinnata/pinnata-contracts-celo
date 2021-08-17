from brownie import (
    accounts, ERC20KP3ROracle, UniswapV2Oracle, BalancerPairOracle, ProxyOracle, CoreOracle,
    HomoraBank, CurveOracle, UniswapV2SpellV1, WERC20, WLiquidityGauge, WMasterChef,
    WStakingRewards, SushiswapSpellV1, BalancerSpellV1, CurveSpellV1, UbeswapV1Oracle, SafeBox
)
from brownie import interface
from .utils import *
import json
import time

def main():
    deployer = accounts.load('admin')
    f = open('scripts/dahlia_addresses.json')
    addr = json.load(f)['mainnet']
    
    ubeswap_oracle = UbeswapV1Oracle.at(addr['ube_oracle'])

    while True:
        if ubeswap_oracle.workable():
            ubeswap_oracle.work({'from': deployer})
        else:
            print("no work")

        time.sleep(120)

    print('Done!')