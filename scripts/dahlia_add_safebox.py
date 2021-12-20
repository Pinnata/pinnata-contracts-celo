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
    sub_addr = addr.get('alpha')

    celo = interface.IERC20Ex(sub_addr.get('celo'))
    ube = interface.IERC20Ex(sub_addr.get('ube'))
    mobi = interface.IERC20Ex(sub_addr.get('mobi'))
    fcelo = interface.IERC20Ex(sub_addr.get('fcelo'))
    fube = interface.IERC20Ex(sub_addr.get('fube'))
    fmobi = interface.IERC20Ex(sub_addr.get('fmobi'))
    dahlia_bank = Contract.from_abi("HomoraBank", sub_addr.get('dahlia_bank'), HomoraBank.abi)

    # deploy safeboxes
    dcelo = SafeBox.deploy(
      fcelo, 'Interest Bearing CELO', 'dCELO', {'from': deployer})
    dmobi = SafeBox.deploy(
      fmobi, 'Interest Bearing MOBI', 'dMOBI', {'from': deployer})
    dube = SafeBox.deploy(
      fube, 'Interest Bearing UBE', 'dUBE', {'from': deployer})
    
    # add banks
    dahlia_bank.addBank(celo, fcelo, {'from': deployer})
    dahlia_bank.addBank(ube, fube, {'from': deployer})
    dahlia_bank.addBank(mobi, fmobi, {'from': deployer})

    dahlia_bank.setWhitelistTokens([celo, ube, mobi], [True, True, True], {'from': deployer})

    addr.get('alpha').update({
        'dcelo': dcelo.address,
        'dube': dube.address,
        'dmobi': dmobi.address,
    })

    print(json.dumps(addr, indent=4), file=open('scripts/dahlia_addresses.json', 'w'))