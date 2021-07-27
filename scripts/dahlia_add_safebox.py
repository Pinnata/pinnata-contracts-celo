from brownie import (
    accounts, HomoraBank, SafeBox
)
from brownie import interface
from .utils import *
import json

def main():
    deployer = accounts.load('admin')
    f = open('scripts/dahlia_addresses.json')
    addr = json.load(f)['mainnet']

    mzpn = interface.IERC20Ex(addr['mzpn'])
    fmzpn = interface.IERC20Ex(addr['fbtc'])
    dahlia_bank = HomoraBank.at(addr['dahlia_bank'])

    # # deploy safeboxes

    SafeBox.deploy(
        fmzpn, 'Interest Bearing Marzipan', 'dMZPN', {'from': deployer})
    
    # add banks
    dahlia_bank.addBank(mzpn, fmzpn, {'from': deployer})

    dahlia_bank.setWhitelistTokens([mzpn], [True], {'from': deployer})

    print('Done!')
