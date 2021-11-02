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
    mainnet_addr = addr.get('mainnet')

    celo = interface.IERC20Ex(mainnet_addr.get('celo'))
    wminichef = WMiniChefV2.at(mainnet_addr.get('wminichef'))
    rewarder = mainnet_addr.get('rewarder')

    wrewarder = WComplexTimeRewarder.deploy(rewarder, celo, {'from': deployer})

    wminichef.set(3, wrewarder, {'from': deployer})
    addr.get('mainnet').update({
        'wrewarder': wrewarder.address,
    })

    print(json.dumps(addr, indent=4), file=open('scripts/dahlia_addresses.json', 'w'))
