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
    cycelo = interface.IERC20Ex(addr['cycelo'])
    cyube = interface.IERC20Ex(addr['cyube'])
    cybtc = interface.IERC20Ex(addr['cybtc'])
    dahlia_bank = HomoraBank.at(addr['dahlia_bank'])

    # # deploy safeboxes

    SafeBox.deploy(
        cycelo, 'Interest Bearing Celo', 'dCELO', {'from': deployer})
    SafeBox.deploy(
        cyube, 'Interest Bearing UBE', 'dUBE', {'from': deployer})
    SafeBox.deploy(
        cybtc, 'Interest Bearing BTC', 'dBTC', {'from': deployer})
    
    # add banks
    dahlia_bank.addBank(celo, cycelo, {'from': deployer})
    dahlia_bank.addBank(ube, cyube, {'from': deployer})
    dahlia_bank.addBank(btc, cybtc, {'from': deployer})

    dahlia_bank.setWhitelistTokens([celo], [True], {'from': deployer})
    dahlia_bank.setWhitelistTokens([ube], [True], {'from': deployer})
    # dahlia_bank.setWhitelistTokens([btc], [True], {'from': deployer})

    print('Done!')
