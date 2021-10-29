from brownie import (
    accounts,
    HomoraBank,
    SafeBox,
    Contract,
    network,
    interface,
)
import json

network.gas_limit(8000000)

def main():
    deployer = accounts.load('dahlia_admin')

    with open('scripts/dahlia_addresses.json', 'r') as f:
        addr = json.load(f)
    mainnet_addr = addr.get('mainnet')

    cusd = interface.IERC20Ex(mainnet_addr.get('cusd'))
    ceur = interface.IERC20Ex(mainnet_addr.get('ceur'))
    # fcusd = interface.IERC20Ex(mainnet_addr.get('fcusd'))
    # fceur = interface.IERC20Ex(mainnet_addr.get('fceur'))
    dahlia_bank = Contract.from_abi("HomoraBank", mainnet_addr.get('dahlia_bank'), HomoraBank.abi)

    # # deploy safeboxes
    # dcusd = SafeBox.deploy(
    #     fcusd, 'Interest Bearing cUSD', 'dcUSD', {'from': deployer})
    # dceur = SafeBox.deploy(
    #     fceur, 'Interest Bearing cEUR', 'dcEUR', {'from': deployer})
    
    # # add banks
    # dahlia_bank.addBank(cusd, fcusd, {'from': deployer})
    # dahlia_bank.addBank(ceur, fceur, {'from': deployer})


    dahlia_bank.setWhitelistTokens([cusd, ceur], [True, True], {'from': deployer})

    # addr.get('mainnet').update({
    #     'dcusd': dcusd.address,
    #     'dceur': dceur.address,
    # })

    print(json.dumps(addr, indent=4), file=open('scripts/dahlia_addresses.json', 'w'))