from brownie import (
    accounts,
    HomoraBank,
    UbeswapMSRSpellV1,
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
    cusd = interface.IERC20Ex(mainnet_addr.get('mcusd'))
    ceur = interface.IERC20Ex(mainnet_addr.get('mceur'))
    urouter = interface.IUniswapV2Router02(mainnet_addr.get('ube_router'))
    ufactory = interface.IUniswapV2Factory(mainnet_addr.get('ube_factory'))

    werc20 = WERC20.at(mainnet_addr.get('werc20'))
    dahlia_bank = Contract.from_abi("HomoraBank", mainnet_addr.get('dahlia_bank'), HomoraBank.abi)

    ubeswap_spell = UbeswapMSRSpellV1.deploy(
        dahlia_bank, werc20, urouter, celo,
        {'from': deployer},
    )

    ubeswap_spell.getAndApprovePair(celo, cusd, {'from': deployer})
    ubeswap_spell.getAndApprovePair(celo, ceur, {'from': deployer})
    ubeswap_spell.getAndApprovePair(cusd, ceur, {'from': deployer})

    celo_cusd_lp = ufactory.getPair(celo, cusd)
    celo_ceur_lp = ufactory.getPair(celo, ceur)
    cusd_ceur_lp = ufactory.getPair(cusd, ceur)

    ubeswap_spell.setWhitelistLPTokens([celo_cusd_lp, celo_ceur_lp, cusd_ceur_lp], [True, True, True], {'from': deployer})

    dahlia_bank.setWhitelistSpells([ubeswap_spell], [True], {'from': deployer})

    addr.get('mainnet').update({
        'ubeswap_msr_spell': ubeswap_spell.address,
    })

    print(json.dumps(addr, indent=4), file=open('scripts/dahlia_addresses.json', 'w'))
