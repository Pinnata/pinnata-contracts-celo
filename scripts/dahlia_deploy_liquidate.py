from brownie import (
    accounts, DahliaLiquidator
)
import json

def main():
    deployer = accounts.load('dahlia_admin')

    with open('scripts/test_address.json', 'r') as f:
        addr = json.load(f)

    DahliaLiquidator.deploy(
        addr.get('mainnet').get('ube_router'),
        addr.get('mainnet').get('dahlia_bank'),
        addr.get('mainnet').get('werc20'),
        {"from": deployer}
    )

    addr.get('mainnet').update({
        'dahlia_liquidator': DahliaLiquidator.address,
    })

    print(json.dumps(addr, indent=4), file=open('scripts/test_address.json', 'w'))