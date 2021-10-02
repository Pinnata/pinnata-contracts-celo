from brownie import accounts, interface, Contract
from brownie import (
    HomoraBank, ProxyOracle, CoreOracle, UniswapV2Oracle, SimpleOracle, UniswapV2SpellV1, WERC20, SafeBox, WStakingRewards, network
)
import json



def main():
    kyle = accounts.load('kyle_personal')
    f = open('scripts/dahlia_addresses.json')
    addr = json.load(f)['mainnet']

    celo = interface.IERC20Ex(addr['celo'])
    mcusd = interface.IERC20Ex(addr['mcusd'])
    dahlia_bank = Contract.from_abi("HomoraBank", addr.get('dahlia_bank'), HomoraBank.abi)
    uniswap_spell = UniswapV2SpellV1.at(addr['uni_spell'])
    wstaking = WStakingRewards.at(addr['celo_ube_wstaking'])
    bytes = uniswap_spell.addLiquidityWStakingRewards.encode_input(
            celo.address,
            mcusd.address,
            ["3000000000000000000",
             0,
             0,
             "1051000000000000000",
             "52388000000000000000",
             0,
             0,
             0],
            wstaking
        )

    print(bytes)

    # open a position
    dahlia_bank.execute(
        0,
        uniswap_spell,
        bytes,
        {
            'from': kyle, 
        }
    )
