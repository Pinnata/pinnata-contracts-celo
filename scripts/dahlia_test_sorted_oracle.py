from brownie import (
    CeloProxyPriceProvider,
    accounts,
    network,
)
import json

network.gas_limit(8000000)

def main():
    zero_add = '0x0000000000000000000000000000000000000000'
    deployer = accounts.load('dahlia_admin')

    f = open('scripts/dahlia_addresses.json')
    addr = json.load(f)['alfajores']

    celo = addr['celo']
    cusd = addr['cusd']
    ceur = addr['ceur']
    oracle = CeloProxyPriceProvider.deploy(zero_add, {'from': deployer})
    print("celo", oracle.getAssetPrice(celo))
    print('cusd', oracle.getAssetPrice(cusd))
    print('ceur', oracle.getAssetPrice(ceur))
