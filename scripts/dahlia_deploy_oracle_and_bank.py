from brownie import (
    accounts, ProxyOracle, 
    CoreOracle, HomoraBank
)
import json

def main():
    deployer = accounts.load('dahlia_admin')

    with open('scripts/dahlia_addresses.json', 'r') as f:
        addr = json.load(f)

    core_oracle = CoreOracle.deploy({'from': deployer})
    proxy_oracle = ProxyOracle.deploy(core_oracle, {'from': deployer})

    bank = HomoraBank.deploy({'from': deployer})
    bank.initialize(proxy_oracle, 0, {'from': deployer})

    addr.get('mainnet').update({
        'core_oracle': core_oracle.address,
        'proxy_oracle': proxy_oracle.address,
        'dahlia_bank': bank.address, 
    })

    print(json.dumps(addr, indent=4), file=open('scripts/dahlia_addresses.json', 'w'))