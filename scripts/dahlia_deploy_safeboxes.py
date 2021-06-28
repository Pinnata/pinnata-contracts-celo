from brownie import (
    accounts, HomoraBank, SafeBox
)
from brownie import interface
from .utils import *

def main():
    # deployer = accounts.at('0xB593d82d53e2c187dc49673709a6E9f806cdC835', force=True)
    deployer = accounts.load('gh')

    celo_addr = '0xf194afdf50b03e69bd7d057c1aa9e10c9954e4c9'
    ube_addr = '0xbe413cdfdad27e71cf533882c760a91ecd02ab27'
    btc_addr = '0xd629eb00deced2a080b7ec630ef6ac117e614f1b'
    cycelo_addr = '0xB01BCdB6e90C216Ee2Cb15bF97B97283c70932d6'
    cyube_addr = '0x60403187a1850688deE07C8BdeBE4355Ced1d081'
    cybtc_addr = ''
    dahlia_bank_addr = '0x8772D538785f9dc2a8b1356D4550320E93f4A616'

    celo = interface.IERC20Ex(celo_addr)
    ube = interface.IERC20Ex(ube_addr)
    btc = interface.IERC20Ex(btc_addr)
    cycelo = interface.IERC20Ex(cycelo_addr)
    cyube = interface.IERC20Ex(cyube_addr)
    cybtc = interface.IERC20Ex(cybtc_addr)
    dahlia_bank = HomoraBank.at(dahlia_bank_addr)

    # deploy safeboxes

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

    dahlia_bank.setWhitelistTokens([celo, ube, btc], [True, True, True], {'from': deployer})

    print('Done!')
