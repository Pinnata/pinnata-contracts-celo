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

    celo = interface.IERC20Ex(addr['celo'])
    ube = interface.IERC20Ex(addr['ube'])
    btc = interface.IERC20Ex(addr['btc'])
    fcelo = interface.IERC20Ex(addr['fcelo'])
    fube = interface.IERC20Ex(addr['fube'])
    fbtc = interface.IERC20Ex(addr['fbtc'])
    dahlia_bank = HomoraBank.at(addr['dahlia_bank'])

    # # deploy safeboxes

    SafeBox.deploy(
        fcelo, 'Interest Bearing Celo', 'dCELO', {'from': deployer})
    SafeBox.deploy(
        fube, 'Interest Bearing UBE', 'dUBE', {'from': deployer})
    SafeBox.deploy(
        fbtc, 'Interest Bearing BTC', 'dBTC', {'from': deployer})
    
    # add banks
    dahlia_bank.addBank(celo, fcelo, {'from': deployer})
    dahlia_bank.addBank(ube, fube, {'from': deployer})
    dahlia_bank.addBank(btc, fbtc, {'from': deployer})

    dahlia_bank.setWhitelistTokens([celo], [True], {'from': deployer})
    dahlia_bank.setWhitelistTokens([ube], [True], {'from': deployer})
    dahlia_bank.setWhitelistTokens([btc], [True], {'from': deployer})

    print('Done!')
