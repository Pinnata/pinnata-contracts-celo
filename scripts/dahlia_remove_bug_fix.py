from brownie import accounts, interface, Contract
from brownie import (
    HomoraBank, ProxyOracle, CoreOracle, UniswapV2Oracle, SimpleOracle, UniswapV2SpellV1, WERC20, SafeBox, WStakingRewards
)
import json


def main():
    kyle = accounts.load('kyle_personal')
    f = open('scripts/dahlia_addresses.json')
    addr = json.load(f)['mainnet']

    celo = interface.IERC20Ex(addr['celo'])
    scelo = interface.IERC20Ex(addr['scelo'])
    ube = interface.IERC20Ex(addr['ube'])

    dahlia_bank = HomoraBank.at(addr['dahlia_bank'])
    uniswap_spell = UniswapV2SpellV1.at(addr['uni_spell'])
    wstaking = WStakingRewards.at(addr['celo_ube_wstaking'])
    id = dahlia_bank.nextPositionId()
    print(id)

    # close the position
    dahlia_bank.execute(
        id-1,
        uniswap_spell,
        uniswap_spell.removeLiquidityWStakingRewards.encode_input(
            celo,
            ube,
            [2**256-1,
             0,
             2**256-1,
             2**256-1,
             0,
             0,
             0],
            wstaking
        ),
        {'from': kyle}
    )