from brownie import (
    accounts, HomoraBank, SafeBox
)
from brownie import interface
from .utils import *
import json

def main():
    deployer = accounts.load('gh')
    f = open('scripts/dahlia_addresses.json')
    addr = json.load(f)['alfajores']

    celo = interface.IERC20Ex(addr['celo'])
    ube = interface.IERC20Ex(addr['ube'])
    cycelo = interface.IERC20Ex(addr['cycelo'])
    cyube = interface.IERC20Ex(addr['cyube'])
    dahlia_bank = HomoraBank.at(addr['dahlia_bank'])

    # deploy safeboxes

    SafeBox.deploy(
        cycelo, 'Interest Bearing Celo', 'dCELO', {'from': deployer})
    SafeBox.deploy(
        cyube, 'Interest Bearing UBE', 'dUBE', {'from': deployer})

    # add banks
    # dahlia_bank.addBank(celo, cycelo, {'from': deployer})
    # dahlia_bank.addBank(ube, cyube, {'from': deployer})

    dahlia_bank.setWhitelistTokens([celo, ube], [True, True], {'from': deployer})

    print('Done!')
