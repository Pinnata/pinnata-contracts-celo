from brownie import (
    accounts, UbeswapV1Oracle, network
)
import json
import time

network.gas_limit(8000000)


def repeat(f, *args):
    """
    Repeat when geth is not broadcasting (unaccounted error)
    """
    while True:
        try:
            return f(*args)
        except KeyError:
            continue



def main():
    deployer = accounts.load('oracle_updater')
    with open('scripts/dahlia_addresses.json', 'r') as f:
        addr = json.load(f)
    mainnet_addr = addr.get('mainnet')

    ubeswap_oracle = UbeswapV1Oracle.at(mainnet_addr.get('ube_oracle'))

    while True:
        if repeat(ubeswap_oracle.workable):
            repeat(ubeswap_oracle.work, {'from': deployer})
        else:
            print("no work")
            
        time.sleep(60)
