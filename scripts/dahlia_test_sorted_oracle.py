from brownie import (
    CeloProxyPriceProvider,
    accounts,
    network,
    MoolaProxyOracle,
)
import json

network.gas_limit(8000000)

def main():
    deployer = accounts.load('dahlia_admin')

    f = open('scripts/dahlia_addresses.json')
    addr = json.load(f)['mainnet']

    celo = addr['celo']
    cusd = addr['cusd']
    ceur = addr['ceur']
    mcusd = addr['mcusd']
    mceur = addr['mceur']
    oracle = CeloProxyPriceProvider.deploy({'from': deployer})
    print("celo", oracle.getCELOPx(celo))
    print('cusd', oracle.getCELOPx(cusd))
    print('ceur', oracle.getCELOPx(ceur))
    moola_proxy = MoolaProxyOracle.deploy(oracle, {'from': deployer})
    print("mcusd", moola_proxy.getCELOPx(mcusd))
    print("mceur", moola_proxy.getCELOPx(mceur))
