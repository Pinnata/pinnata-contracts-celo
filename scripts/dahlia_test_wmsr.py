from os import EX_CANTCREAT
from brownie import (
    accounts,
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
    alfajores_addr = addr.get('alfajores')

    celo = interface.IERC20Ex(alfajores_addr.get('celo'))
    cusd = interface.IERC20Ex(alfajores_addr.get('cusd'))
    ufactory = interface.IUniswapV2Factory(alfajores_addr.get('ufactory'))
    celo_cusd_lp = interface.IERC20Ex(ufactory.getPair(celo, cusd))
    celo_cusd_wmstaking = interface.IWMStakingRewards(alfajores_addr.get('celo_cusd_wmstaking'))

    print(celo_cusd_wmstaking.getReward())

    # celo_ube_wmstaking.mint(1000, {'from': alice})
    # time.sleep(300)

    # celo_ube_wmstaking.burn(10, 2**256-1, {'from': alice})

    # postCelo = celo.balanceOf(alice)
    # postUbe = ube.balanceOf(alice)

    # print(postCelo, prevCelo)
    # print(postUbe, prevUbe)
