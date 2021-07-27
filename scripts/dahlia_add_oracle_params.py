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
    addr = json.load(f)['mainnet']

    core_oracle = CoreOracle.at(addr['core_oracle'])
    proxy_oracle = ProxyOracle.at(addr['proxy_oracle'])
    celo = interface.IERC20Ex(addr['celo'])
    cusd = interface.IERC20Ex(addr['cusd'])
    ceur = interface.IERC20Ex(addr['ceur'])
    mzpn = interface.IERC20Ex(addr['mzpn'])
    ube_router = interface.IUniswapV2Router02(addr['ube_router'])
    uni_oracle = UniswapV2Oracle.at(addr['uni_oracle'])
    ubeswap_oracle = UbeswapV1Oracle.at(addr['ube_oracle'])
    kp3r_oracle = ERC20KP3ROracle.at(addr['kp3r_oracle'])

    ubeswap_oracle.addPair(celo, cusd, {'from': deployer})
    ubeswap_oracle.addPair(celo, ceur, {'from': deployer})
    ubeswap_oracle.addPair(celo, mzpn, {'from': deployer})

    ube_factory_address = ube_router.factory({'from': deployer})
    ube_factory = interface.IUniswapV2Factory(ube_factory_address)

    celo_mzpn_lp = ube_factory.getPair(celo, mzpn)
    cusd_mzpn_lp = ube_factory.getPair(cusd, mzpn)
    ceur_mzpn_lp = ube_factory.getPair(ceur, mzpn)
    celo_cusd_lp = ube_factory.getPair(celo, cusd)

    core_oracle.setRoute([
        mzpn,
        cusd,
        ceur,
        celo_mzpn_lp,
        cusd_mzpn_lp,
        ceur_mzpn_lp,
        celo_cusd_lp,
    ], [
        kp3r_oracle,
        kp3r_oracle,
        kp3r_oracle,
        uni_oracle,
        uni_oracle,
        uni_oracle,
        uni_oracle,
    ], {'from': deployer})

    proxy_oracle.setTokenFactors([
        mzpn,
        cusd,
        ceur,
        celo_mzpn_lp,
        cusd_mzpn_lp,
        ceur_mzpn_lp,
        celo_cusd_lp,
    ], [
        [13000, 7800, 10250],
        [11000, 9000, 10250],
        [11000, 9000, 10250],
        [50000, 7800, 10250],
        [50000, 7800, 10250],
        [50000, 7800, 10250],
        [50000, 7800, 10250],
    ], {'from': deployer})

    print('Done!')