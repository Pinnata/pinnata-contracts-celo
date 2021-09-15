from brownie import (
    accounts, HomoraBank, SafeBox
)
from brownie import interface
import json

def main():
    deployer = accounts.load('kyle_personal')

    with open('scripts/dahlia_addresses.json', 'r') as f:
        addr = json.load(f)
    mainnet_addr = addr.get('mainnet')

    interface.IERC20Ex(mainnet_addr.get('celo')).approve(mainnet_addr.get('dcelo'), 0, {'from': deployer})
    interface.IERC20Ex(mainnet_addr.get('mcusd')).approve(mainnet_addr.get('dmcusd'), 0, {'from': deployer})
    interface.IERC20Ex(mainnet_addr.get('mceur')).approve(mainnet_addr.get('dmceur'), 0, {'from': deployer})
    interface.IERC20Ex(mainnet_addr.get('ube')).approve(mainnet_addr.get('dube'), 0, {'from': deployer})
    interface.IERC20Ex(mainnet_addr.get('scelo')).approve(mainnet_addr.get('dscelo'), 0, {'from': deployer})