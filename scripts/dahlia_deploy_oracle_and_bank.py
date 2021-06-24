from brownie import (
    accounts, ERC20KP3ROracle, UniswapV2Oracle, BalancerPairOracle, ProxyOracle, CoreOracle,
    HomoraBank, CurveOracle, UniswapV2SpellV1, WERC20, WLiquidityGauge, WMasterChef,
    WStakingRewards, SushiswapSpellV1, BalancerSpellV1, CurveSpellV1, UbeswapV1Oracle, SafeBox
)
from brownie import interface
from .utils import *

def main():
    deployer = accounts.load('gh')

    core_oracle = CoreOracle.deploy({'from': deployer})
    proxy_oracle = ProxyOracle.deploy(core_oracle, {'from': deployer})

    # TODO: use proxy openzeppelin contract
    # bank_impl = HomoraBank.deploy({'from': deployer})
    # bank_impl.initialize(proxy_oracle, 0, {'from': deployer})
    # bank = TransparentUpgradableProxy(bank_impl, deployer, {'from': deployer})
    
    bank = HomoraBank.deploy({'from': deployer})
    bank.initialize(proxy_oracle, 0, {'from': deployer})

    print('Done!')