from brownie import (
    CeloProxyPriceProvider,
    MoolaProxyOracle,
    accounts,
    network,
)
import json

network.gas_limit(8000000)

def main():
    deployer = accounts.load('dahlia_admin')

    f = open('scripts/dahlia_addresses.json')
    addr = json.load(f)['mainnet']

    celo = addr['celo']
    mcusd = addr['mcusd']
    mceur = addr['mceur']
    sorted_oracle = CeloProxyPriceProvider.deploy({'from': deployer})
    moola_oracle = MoolaProxyOracle.deploy(sorted_oracle, {'from': deployer})
    print("celo", sorted_oracle.getCELOPx(celo))
    print('mcusd', moola_oracle.getCELOPx(mcusd))
    print('mceur', moola_oracle.getCELOPx(mceur))
