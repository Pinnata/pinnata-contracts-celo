from brownie import (
    accounts, HomoraBank, UniswapV2SpellV1, WERC20, Contract, network
)
from brownie import interface
import json

network.gas_limit(8000000)

def main():
    deployer = accounts.load('dahlia_admin')

    with open('scripts/dahlia_addresses.json', 'r') as f:
        addr = json.load(f)
    alfajores_addr = addr.get('alfajores')

    celo = interface.IERC20Ex(alfajores_addr.get('celo'))
    cusd = interface.IERC20Ex(alfajores_addr.get('cusd'))
    ceur = interface.IERC20Ex(alfajores_addr.get('ceur'))
    urouter = interface.IUniswapV2Router02(alfajores_addr.get('urouter'))
    ufactory = interface.IUniswapV2Factory(alfajores_addr.get('ufactory'))

    werc20 = WERC20.at(alfajores_addr.get('werc20'))
    dahlia_bank = Contract.from_abi("HomoraBank", alfajores_addr.get('dahlia_bank'), HomoraBank.abi)

    uniswap_spell = UniswapV2SpellV1.deploy(
        dahlia_bank, werc20, urouter, celo,
        {'from': deployer},
    )

    uniswap_spell.getAndApprovePair(celo, cusd, {'from': deployer})
    uniswap_spell.getAndApprovePair(celo, ceur, {'from': deployer})
    uniswap_spell.getAndApprovePair(cusd, ceur, {'from': deployer})

    celo_cusd_lp = ufactory.getPair(celo, cusd)
    celo_ceur_lp = ufactory.getPair(celo, ceur)
    cusd_ceur_lp = ufactory.getPair(cusd, ceur)

    uniswap_spell.setWhitelistLPTokens([celo_cusd_lp, celo_ceur_lp, cusd_ceur_lp], [True, True, True], {'from': deployer})

    dahlia_bank.setWhitelistSpells([uniswap_spell], [True], {'from': deployer})

    addr.get('alfajores').update({
        'uni_spell': uniswap_spell.address,
    })

    print(json.dumps(addr, indent=4), file=open('scripts/dahlia_addresses.json', 'w'))
