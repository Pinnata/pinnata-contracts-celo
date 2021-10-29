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
    mainnet_addr = addr.get('mainnet')

    celo = interface.IERC20Ex(mainnet_addr.get('celo'))
    cusd = interface.IERC20Ex(mainnet_addr.get('cusd'))
    ceur = interface.IERC20Ex(mainnet_addr.get('ceur'))
    sushi_router = interface.IUniswapV2Router02(mainnet_addr.get('sushi_router'))
    sushi_factory = interface.IUniswapV2Factory(mainnet_addr.get('sushi_factory'))
    wminichef = mainnet_addr.get('wminichef')

    werc20 = WERC20.at(mainnet_addr.get('werc20'))
    dahlia_bank = Contract.from_abi("HomoraBank", mainnet_addr.get('dahlia_bank'), HomoraBank.abi)

    sushi_spell = SushiswapSpellV1.deploy(
        dahlia_bank, werc20, sushi_router, wminichef, celo,
        {'from': deployer},
    )

    sushi_spell.getAndApprovePair(cusd, ceur, {'from': deployer})

    cusd_ceur_lp = sushi_factory.getPair(cusd, ceur)

    sushi_spell.setWhitelistLPTokens([cusd_ceur_lp], [True], {'from': deployer})

    dahlia_bank.setWhitelistSpells([sushi_spell], [True], {'from': deployer})

    addr.get('mainnet').update({
        'sushi_spell': sushi_spell.address,
    })

    print(json.dumps(addr, indent=4), file=open('scripts/dahlia_addresses.json', 'w'))
