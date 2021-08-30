from brownie import (
    accounts, UbeswapV1Oracle
)
import json
import time

def main():
    deployer = accounts.load('dahlia_admin')
    with open('scripts/test_address.json', 'r') as f:
        addr = json.load(f)
    mainnet_addr.get('mainnet')

    ubeswap_oracle = UbeswapV1Oracle.at(mainnet_addr.get('ube_oracle'))

    while True:
        if ubeswap_oracle.workable():
            ubeswap_oracle.work({'from': deployer})
            print("work")
        else:
            print("no work")
            
        time.sleep(60)