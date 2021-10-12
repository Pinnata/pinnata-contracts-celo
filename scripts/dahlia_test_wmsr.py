from os import EX_CANTCREAT
from brownie import (
    accounts,
    WMoolaStakingRewards, 
    ProxyOracle,
    interface,
    network
)

import json
import time

network.gas_limit(8000000)


def main():
    alice = accounts.load('dahlia_alice')

    with open('scripts/dahlia_addresses.json', 'r') as f:
        addr = json.load(f)
    mainnet_addr = addr.get('mainnet')

    celo = interface.IERC20Ex(mainnet_addr.get('celo'))
    ube = interface.IERC20Ex(mainnet_addr.get('ube'))
    ube_factory = interface.IUniswapV2Factory(mainnet_addr.get('ube_factory'))
    celo_ube_lp = interface.IERC20Ex(ube_factory.getPair(celo, ube))
    celo_ube_wmstaking = WMoolaStakingRewards.at(mainnet_addr.get('celo_ube_wmstaking'))

    prevCelo = celo.balanceOf(alice)
    prevUbe = ube.balanceOf(alice)

    celo_ube_wmstaking.mint(1000, {'from': alice})
    time.sleep(300)

    celo_ube_wmstaking.burn(10, 2**256-1, {'from': alice})

    postCelo = celo.balanceOf(alice)
    postUbe = ube.balanceOf(alice)

    print(postCelo, prevCelo)
    print(postUbe, prevUbe)
