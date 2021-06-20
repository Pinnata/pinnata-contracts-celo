from brownie import (
    accounts, ERC20KP3ROracle, UniswapV2Oracle, BalancerPairOracle, ProxyOracle, CoreOracle,
    HomoraBank, CurveOracle, UniswapV2SpellV1, WERC20, WLiquidityGauge, WMasterChef,
    WStakingRewards, SushiswapSpellV1, BalancerSpellV1, CurveSpellV1, UbeswapV1Oracle, SafeBox
)
from brownie import interface
from .utils import *

def main():
    deployer = accounts.load('gh')

    core_oracle_addr = '0x384f6e069aC3726E1894A30D0d46021c5f5E8acA'
    proxy_oracle_addr = '0x31ac8Ac2BC3025de9aA9f3EC5dC9db2dc1B5A6E3'
    celo_addr = '0xf194afdf50b03e69bd7d057c1aa9e10c9954e4c9'
    cusd_addr = '0x874069fa1eb16d44d622f2e0ca25eea172369bc1'
    ube_addr = '0xbe413cdfdad27e71cf533882c760a91ecd02ab27'
    ube_router_addr = '0xE3D8bd6Aed4F159bc8000a9cD47CffDb95F96121'

    core_oracle = CoreOracle.at(core_oracle_addr)
    proxy_oracle = ProxyOracle.at(proxy_oracle_addr)
    celo = interface.IERC20Ex(celo_addr)
    cusd = interface.IERC20Ex(cusd_addr)
    ube = interface.IERC20Ex(ube_addr)
    ube_router = interface.IUniswapV2Router02(ube_router_addr)

    uni_oracle = UniswapV2Oracle.deploy(core_oracle, {'from': deployer})
    ubeswap_oracle = UbeswapV1Oracle.deploy({'from': deployer})

    ubeswap_oracle.addPair(celo_addr, cusd_addr)
    ubeswap_oracle.addPair(celo_addr, ube_addr)

    kp3r_oracle = ERC20KP3ROracle.deploy(ubeswap_oracle, {'from': deployer})

    ube_factory_address = ube_router.factory({'from': deployer})
    ube_factory = interface.IUniswapV2Factory(ube_factory_address)

    celo_cusd_lp = ube_factory.getPair(celo, cusd)
    celo_ube_lp = ube_factory.getPair(celo, ube)

    core_oracle.setRoute([
        celo_addr,
        cusd_addr,
        ube_addr,
        celo_cusd_lp,
        celo_ube_lp,
    ], [
        kp3r_oracle,
        kp3r_oracle,
        kp3r_oracle,
        uni_oracle,
        uni_oracle,
    ], {'from': deployer})

    proxy_oracle.setTokenFactors([
        celo_addr,
        cusd_addr,
        ube_addr,
        celo_cusd_lp,
        celo_ube_lp,
    ], [
        [12500, 8000, 10250],
        [10500, 9500, 10250],
        [12500, 8000, 10250],
        [50000, 0, 10250],
        [50000, 0, 10250],
    ], {'from': deployer})

    werc20 = WERC20.deploy({'from': deployer})

    proxy_oracle.setWhitelistERC1155(
        [werc20],
        True,
        {'from': deployer},
    )

    print('Done!')