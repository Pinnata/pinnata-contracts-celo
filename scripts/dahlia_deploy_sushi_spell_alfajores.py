from brownie import (
    accounts,
    HomoraBank,
    SushiswapSpellV1,
    WERC20,
    Contract,
    network,
    interface,
)
import json

network.gas_limit(8000000)

def main():
    deployer = accounts.load('dahlia_admin')

    with open('scripts/dahlia_addresses.json', 'r') as f:
        addr = json.load(f)
    alfajores_addr = addr.get('alfajores')

    celo = interface.IERC20Ex(alfajores_addr.get('celo'))
    cusd = interface.IERC20Ex(alfajores_addr.get('cusd'))
    mock2 = interface.IERC20Ex(alfajores_addr.get('mock2'))
    sushi_router = interface.IUniswapV2Router02(alfajores_addr.get('urouter'))
    sushi_factory = interface.IUniswapV2Factory(alfajores_addr.get('ufactory'))
    wminichef = alfajores_addr.get('wminichef')

    werc20 = WERC20.at(alfajores_addr.get('werc20'))
    dahlia_bank = Contract.from_abi("HomoraBank", alfajores_addr.get('dahlia_bank'), HomoraBank.abi)

    sushi_spell = SushiswapSpellV1.deploy(
        dahlia_bank, werc20, sushi_router, wminichef, celo, mock2,
        {'from': deployer},
    )

    sushi_spell.getAndApprovePair(celo, cusd, {'from': deployer})

    celo_cusd_lp = sushi_factory.getPair(celo, cusd)

    sushi_spell.setWhitelistLPTokens([celo_cusd_lp], [True], {'from': deployer})

    dahlia_bank.setWhitelistSpells([sushi_spell], [True], {'from': deployer})

    addr.get('alfajores').update({
        'sushi_spell': sushi_spell.address,
    })

    print(json.dumps(addr, indent=4), file=open('scripts/dahlia_addresses.json', 'w'))
