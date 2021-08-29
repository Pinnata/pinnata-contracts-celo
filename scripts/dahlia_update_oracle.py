from brownie import (
    accounts, UbeswapV1Oracle
)
import json

def main():
    deployer = accounts.load('dahlia_admin')
    f = open('scripts/dahlia_addresses.json')
    addr = json.load(f)['mainnet']

    ubeswap_oracle = UbeswapV1Oracle.at(addr['ube_oracle'])

    if ubeswap_oracle.workable():
        ubeswap_oracle.work({'from': deployer})
        print("work")
    else:
        print("no work")

    print('Done!')