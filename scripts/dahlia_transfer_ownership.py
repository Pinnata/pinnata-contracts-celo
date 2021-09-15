from brownie import (
    accounts, UbeswapV1Oracle, network
)
import json

network.gas_limit(8000000)


def main():
    deployer = accounts.load('dahlia_admin')

    with open('scripts/dahlia_addresses.json', 'r') as f:
        addr = json.load(f)
    mainnet_addr = addr.get('mainnet')

    ubeswap_oracle = UbeswapV1Oracle.at(mainnet_addr.get('ube_oracle'))

    ubeswap_oracle.transferOwnership("0x08B7a5d1c4b9B711F597994052f2050ba0cc3a7e", {"from": deployer})