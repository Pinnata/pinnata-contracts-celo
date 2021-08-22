from brownie import (
    accounts, ERC20KP3ROracle, CoreOracle,
    CurveOracle, WERC20, UbeswapV1Oracle, HomoraBank, UniswapV2SpellV1, SafeBox,
    SimpleOracle
)
from brownie import interface
from .utils import *
import json

def main():
    deployer = accounts.load('admin')

    f = open('scripts/dahlia_addresses.json')
    addr = json.load(f)['mainnet']

    ube = interface.IERC20Ex(addr['ube'])
    core_oracle = CoreOracle.at(addr['core_oracle'])
    kp3r_oracle = ERC20KP3ROracle.at(addr['kp3r_oracle'])

    core_oracle.setRoute([
        ube,
    ], [
        kp3r_oracle,
    ], {'from': deployer})

    print('Done!')