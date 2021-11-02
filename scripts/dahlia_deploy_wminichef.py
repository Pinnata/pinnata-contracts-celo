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
    mainnet_addr = addr.get('mainnet')

    proxy_oracle = ProxyOracle.at(mainnet_addr.get('proxy_oracle'))
    minichef = mainnet_addr.get('minichef')

    wminichef = WMiniChefV2.deploy(
        minichef,
        {'from': deployer}
    )

    proxy_oracle.setWhitelistERC1155(
        [wminichef],
        True,
        {'from': deployer},
    )
    
    addr.get('mainnet').update({
        'wminichef': wminichef.address,
    })

    print(json.dumps(addr, indent=4), file=open('scripts/dahlia_addresses.json', 'w'))