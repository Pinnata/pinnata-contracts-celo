from brownie import (
    accounts, HomoraBank, UniswapV2SpellV1, WERC20, WStakingRewards, ProxyOracle
)
from brownie import interface
from .utils import *
import json

def main():
    deployer = accounts.load('admin')
    f = open('scripts/dahlia_addresses.json')
    addr = json.load(f)['mainnet']

    ube_celo_w_staking = WStakingRewards.at(addr['ube_celo_w_staking'])
    proxy_oracle = ProxyOracle.at(addr['proxy_oracle'])


    # ube_factory = interface.IUniswapV2Factory(addr['ube_factory'])

    # celo_ube_lp = ube_factory.getPair(celo, ube)


    # wstaking = WStakingRewards.deploy(
    #     addr['ube_celo_staking'],
    #     celo_ube_lp,
    #     ube,
    #     {'from': deployer}
    # )

    proxy_oracle.setWhitelistERC1155(
        [ube_celo_w_staking],
        True,
        {'from': deployer},
    )

    print('Done!')
