from brownie import (
    accounts, DahliaLiquidator, network
)
import json

network.gas_limit(8000000)

def main():
    deployer = accounts.load('dahlia_admin')

    with open('scripts/dahlia_addresses.json', 'r') as f:
        addr = json.load(f)

    mainnet_addr = addr.get('mainnet')

    liquid = DahliaLiquidator.deploy(
        mainnet_addr.get('ube_router'),
        mainnet_addr.get('dahlia_bank'),
        mainnet_addr.get('werc20'),
        {"from": deployer}
    )

    addr.get('mainnet').update({
        'dahlia_liquidator': liquid.address,
    })

    print(json.dumps(addr, indent=4), file=open('scripts/dahlia_addresses.json', 'w'))