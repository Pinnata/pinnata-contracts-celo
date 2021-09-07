from brownie import (
    accounts, UbeswapV1Oracle
)
import json

def main():
    deployer = accounts.load('dahlia_admin')

    with open('scripts/dahlia_addresses.json', 'r') as f:
        addr = json.load(f)
    mainnet_addr = addr.get('mainnet')

    ubeswap_oracle = UbeswapV1Oracle.at(mainnet_addr.get('ube_oracle'))

    if ubeswap_oracle.workable():
        ubeswap_oracle.work({'from': deployer})
        print("work")
    else:
        print("no work")

    print('Done!')