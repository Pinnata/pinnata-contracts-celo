from brownie import (
    accounts,
    network,
    interface,
    WComplexTimeRewarder,
    WMiniChefV2
)
import json

network.gas_limit(8000000)

def main():
    deployer = accounts.load('dahlia_admin')

    with open('scripts/dahlia_addresses.json', 'r') as f:
        addr = json.load(f)
    alfajores_addr = addr.get('alfajores')

    mock2 = interface.IERC20Ex(alfajores_addr.get('mock2'))
    wminichef = WMiniChefV2.at(alfajores_addr.get('wminichef'))
    rewarder = alfajores_addr.get('rewarder')

    wrewarder = WComplexTimeRewarder.deploy(rewarder, mock2, {'from': deployer})

    wminichef.set(1, wrewarder, {'from': deployer})
    addr.get('alfajores').update({
        'wrewarder': wrewarder.address,
    })

    print(json.dumps(addr, indent=4), file=open('scripts/dahlia_addresses.json', 'w'))
