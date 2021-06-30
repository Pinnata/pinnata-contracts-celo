from brownie import (
    accounts, ERC20KP3ROracle, UniswapV2Oracle, ProxyOracle, CoreOracle,
    CurveOracle, WERC20, UbeswapV1Oracle
)
from brownie import interface
from .utils import *
import json

def main():
    deployer = accounts.load('gh')
    f = open('scripts/dahlia_addresses.json')
    addr = json.load(f)['alfajores']

    core_oracle = CoreOracle.at(addr['core_oracle'])
    proxy_oracle = ProxyOracle.at(addr['proxy_oracle'])
    celo = interface.IERC20Ex(addr['celo'])
    ube = interface.IERC20Ex(addr['ube'])
    mcusd = interface.IERC20Ex(addr['mcusd'])
    scelo = interface.IERC20Ex(addr['scelo'])
    ube_router = interface.IUniswapV2Router02(addr['ube_router'])

    uni_oracle = UniswapV2Oracle.deploy(core_oracle, {'from': deployer})
    ubeswap_oracle = UbeswapV1Oracle.deploy({'from': deployer})

    ubeswap_oracle.addPair(celo, ube)
    ubeswap_oracle.addPair(celo, mcusd)
    ubeswap_oracle.addPair(scelo, celo)

    kp3r_oracle = ERC20KP3ROracle.deploy(ubeswap_oracle, {'from': deployer})

    ube_factory_address = ube_router.factory({'from': deployer})
    ube_factory = interface.IUniswapV2Factory(ube_factory_address)

    celo_ube_lp = ube_factory.getPair(celo, ube)
    celo_mcusd_lp = ube_factory.getPair(celo, mcusd)
    scelo_celo_lp = ube_factory.getPair(scelo, celo)

    core_oracle.setRoute([
        celo,
        ube,
        mcusd,
        scelo,
        celo_ube_lp,
        celo_mcusd_lp,
        scelo_celo_lp,
    ], [
        kp3r_oracle,
        kp3r_oracle,
        kp3r_oracle,
        kp3r_oracle,
        uni_oracle,
        uni_oracle,
        uni_oracle,
    ], {'from': deployer})

    proxy_oracle.setTokenFactors([
        celo,
        ube,
        mcusd,
        scelo,
        celo_ube_lp,
        celo_mcusd_lp,
        scelo_celo_lp,
    ], [
        [13000, 7800, 10250],
        [13000, 7800, 10250],
        [11000, 9000, 10250],
        [13000, 7800, 10250],
        [50000, 7800, 10250],
        [50000, 7800, 10250],
        [50000, 7800, 10250],
    ], {'from': deployer})

    werc20 = WERC20.deploy({'from': deployer})

    proxy_oracle.setWhitelistERC1155(
        [werc20],
        True,
        {'from': deployer},
    )

    print('Done!')