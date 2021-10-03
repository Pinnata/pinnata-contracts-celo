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
    alfajores_addr = addr.get('alfajores')

    celo = interface.IERC20Ex(alfajores_addr.get('celo'))
    cusd = interface.IERC20Ex(alfajores_addr.get('cusd'))
    ceur = interface.IERC20Ex(alfajores_addr.get('ceur'))
    fcelo = interface.IERC20Ex(alfajores_addr.get('fcelo'))
    fcusd = interface.IERC20Ex(alfajores_addr.get('fcusd'))
    fceur = interface.IERC20Ex(alfajores_addr.get('fceur'))
    dahlia_bank = Contract.from_abi("HomoraBank", alfajores_addr.get('dahlia_bank'), HomoraBank.abi)

    # deploy safeboxes
    dcelo = SafeBox.deploy(
        fcelo, 'Interest Bearing Celo', 'dCELO', {'from': deployer})
    dcusd = SafeBox.deploy(
        fcusd, 'Interest Bearing mcUSD', 'dcUSD', {'from': deployer})
    dceur = SafeBox.deploy(
        fceur, 'Interest Bearing mcEUR', 'dcEUR', {'from': deployer})
    
    # add banks
    dahlia_bank.addBank(celo, fcelo, {'from': deployer})
    dahlia_bank.addBank(cusd, fcusd, {'from': deployer})
    dahlia_bank.addBank(ceur, fceur, {'from': deployer})

    dahlia_bank.setWhitelistTokens([celo, cusd, ceur], [True, True, True], {'from': deployer})

    addr.get('alfajores').update({
        'dcelo': dcelo.address,
        'dcusd': dcusd.address,
        'dceur': dceur.address,
    })

    print(json.dumps(addr, indent=4), file=open('scripts/dahlia_addresses.json', 'w'))