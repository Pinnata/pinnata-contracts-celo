from brownie import (
    accounts,
    WMiniChefV2, 
    ProxyOracle,
    interface,
    network,
)

import json

network.gas_limit(8000000)

def main():
    deployer = accounts.load('dahlia_admin')

    with open('scripts/dahlia_addresses.json', 'r') as f:
        addr = json.load(f)
    alfajores_addr = addr.get('alfajores')

    celo = interface.IERC20Ex(alfajores_addr.get('celo'))
    proxy_oracle = ProxyOracle.at(alfajores_addr.get('proxy_oracle'))
    minichef = alfajores_addr.get('minichef')

    wminichef = WMiniChefV2.deploy(
        minichef,
        {'from': deployer}
    )

    proxy_oracle.setWhitelistERC1155(
        [wminichef],
        True,
        {'from': deployer},
    )
    
    addr.get('alfajores').update({
        'wminichef': wminichef.address,
    })

    print(json.dumps(addr, indent=4), file=open('scripts/dahlia_addresses.json', 'w'))
