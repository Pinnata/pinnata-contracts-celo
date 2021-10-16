from brownie import (
    CeloProxyPriceProvider,
    accounts,
    network,
)
import json

network.gas_limit(8000000)

def main():
    deployer = accounts.load('dahlia_admin')

    f = open('scripts/dahlia_addresses.json')
    addr = json.load(f)['alfajores']

    celo = addr['celo']
    cusd = addr['cusd']
    ceur = addr['ceur']
    oracle = CeloProxyPriceProvider.deploy({'from': deployer})
    print("celo", oracle.getCELOPx(celo))
    print('cusd', oracle.getCELOPx(cusd))
    print('ceur', oracle.getCELOPx(ceur))
