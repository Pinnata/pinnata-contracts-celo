from brownie import (
    HomoraBank,
    accounts,
    network,
    UniswapV2SpellV1,
    interface,
    WStakingRewards,
    Contract,
)
import json
network.gas_limit(8000000)


def main():
    kyle = accounts.load('kyle_personal')

    with open('scripts/dahlia_addresses.json', 'r') as f:
        addr = json.load(f)

    alfajores_addr = addr.get('alfajores')

    dahlia_bank = Contract.from_abi("HomoraBank", alfajores_addr.get('dahlia_bank'), HomoraBank.abi)
    celo = interface.IERC20Ex(alfajores_addr.get('celo'))
    cusd = interface.IERC20Ex(alfajores_addr.get('cusd'))
    uniswap_spell = UniswapV2SpellV1.at(alfajores_addr.get('uni_spell'))
    wstaking = WStakingRewards.at(alfajores_addr.get('celo_cusd_wstaking'))

    dahlia_bank.execute(
        0,
        uniswap_spell,
        uniswap_spell.addLiquidityWStakingRewards.encode_input(
            cusd,
            celo,
            [
             6*10**16,
             10**16,
             0,
             9*10**16,
             1.5*10**16,
             0,
             0,
             0
            ],
            wstaking
        ),
        {
            'from': kyle, 
        }
    )