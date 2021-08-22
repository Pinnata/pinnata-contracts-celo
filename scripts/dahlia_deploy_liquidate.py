from brownie import (
    accounts, DahliaLiquidator, WERC20, HomoraBank
)
from brownie import interface
from .utils import *
import json

def main():
    deployer = accounts.load('admin')
    f = open('scripts/dahlia_addresses.json')
    addr = json.load(f)['mainnet']

    DahliaLiquidator.deploy(addr['ube_router'], addr['dahlia_bank'], addr['werc20'], {"from": deployer})

    print('Done!')