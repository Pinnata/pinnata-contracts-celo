from brownie import (
    accounts,
    network,
    ProxyOracle,
    CoreOracle,
    HomoraBank,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    Contract
)

import json

network.gas_limit(8000000)

def main():
    deployer = accounts.load('dahlia_admin')

    with open('scripts/dahlia_addresses.json', 'r') as f:
        addr = json.load(f)

    core_oracle = CoreOracle.deploy({'from': deployer})
    proxy_oracle = ProxyOracle.deploy(core_oracle, {'from': deployer})

    bank_impl = HomoraBank.deploy({'from': deployer})
    proxy_admin = ProxyAdmin.deploy({'from': deployer})
    bank = TransparentUpgradeableProxy.deploy(bank_impl.address, proxy_admin.address, b'', {'from': deployer})
    Contract.from_abi("HomoraBank", bank.address, HomoraBank.abi).initialize(proxy_oracle, 10, {'from': deployer})

    addr.get('mainnet').update({
        'core_oracle': core_oracle.address,
        'proxy_oracle': proxy_oracle.address,
        'dahlia_bank': bank.address, 
        'bank_impl': bank_impl.address,
        'proxy_admin': proxy_admin.address,
    })

    print(json.dumps(addr, indent=4), file=open('scripts/dahlia_addresses.json', 'w'))