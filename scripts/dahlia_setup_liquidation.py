from brownie import (
    accounts, ERC20KP3ROracle, UniswapV2Oracle, ProxyOracle, CoreOracle,
    CurveOracle, WERC20, UbeswapV1Oracle, HomoraBank, UniswapV2SpellV1, SafeBox,
    SimpleOracle
)
from brownie import interface
from .utils import *
import json

def main():
    deployer = accounts.load('admin')
    alice = accounts.load('alice')

    f = open('scripts/dahlia_addresses.json')
    addr = json.load(f)['mainnet']

    celo = interface.IERC20Ex(addr['celo'])
    ube = interface.IERC20Ex(addr['ube'])
    dahlia_bank = HomoraBank.at(addr['dahlia_bank'])
    uniswap_spell = UniswapV2SpellV1.at(addr['uniswap_spell'])
    core_oracle = CoreOracle.at(addr['core_oracle'])

    celo.approve(dahlia_bank, 2**256-1, {'from': alice})
    ube.approve(dahlia_bank, 2**256-1, {'from': alice})

    # open a position
    dahlia_bank.execute(
        0,
        uniswap_spell,
        uniswap_spell.addLiquidityWERC20.encode_input(
            celo,
            ube,
            [10**10, # collateral amount celo
             0, # collateral amount ube
             0,
             10**10, # borrow amount celo
             0, # borrow amount ube
             0,
             0,
             0],
        ),
        {
            'from': alice, 
        }
    )

    # market fluctuations
    ubepx = core_oracle.getCELOPx(ube)
    simple_oracle = SimpleOracle.deploy({'from': deployer})
    simple_oracle.setCELOPx([ube], [int(ubepx/10)])

    core_oracle.setRoute([
        ube,
    ], [
        simple_oracle,
    ], {'from': deployer})

    print('Done!')