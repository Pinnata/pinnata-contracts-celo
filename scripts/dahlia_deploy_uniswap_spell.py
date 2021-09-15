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
    mainnet_addr = addr.get('mainnet')

    celo = interface.IERC20Ex(mainnet_addr.get('celo'))
    mcusd = interface.IERC20Ex(mainnet_addr.get('mcusd'))
    mceur = interface.IERC20Ex(mainnet_addr.get('mceur'))
    ube = interface.IERC20Ex(mainnet_addr.get('ube'))
    scelo = interface.IERC20Ex(mainnet_addr.get('scelo'))
    ube_router = interface.IUniswapV2Router02(mainnet_addr.get('ube_router'))
    ube_factory = interface.IUniswapV2Factory(mainnet_addr.get('ube_factory'))
    werc20 = WERC20.at(mainnet_addr.get('werc20'))
    dahlia_bank = Contract.from_abi("HomoraBank", mainnet_addr.get('dahlia_bank'), HomoraBank.abi)

    uniswap_spell = UniswapV2SpellV1.deploy(
        dahlia_bank, werc20, ube_router, celo,
        {'from': deployer},
    )

    uniswap_spell.getAndApprovePair(celo, ube, {'from': deployer})
    uniswap_spell.getAndApprovePair(celo, mcusd, {'from': deployer})
    uniswap_spell.getAndApprovePair(celo, mceur, {'from': deployer})
    uniswap_spell.getAndApprovePair(celo, scelo, {'from': deployer})
    uniswap_spell.getAndApprovePair(mcusd, mceur, {'from': deployer})

    celo_ube_lp = ube_factory.getPair(celo, ube)
    celo_mcusd_lp = ube_factory.getPair(celo, mcusd)
    celo_mceur_lp = ube_factory.getPair(celo, mceur)
    celo_scelo_lp = ube_factory.getPair(celo, scelo)
    mcusd_mceur_lp = ube_factory.getPair(mcusd, mceur)

    uniswap_spell.setWhitelistLPTokens([celo_ube_lp, celo_mcusd_lp, celo_mceur_lp, celo_scelo_lp, mcusd_mceur_lp], [True, True, True, True, True], {'from': deployer})

    dahlia_bank.setWhitelistSpells([uniswap_spell], [True], {'from': deployer})

    addr.get('mainnet').update({
        'uni_spell': uniswap_spell.address,
    })

    print(json.dumps(addr, indent=4), file=open('scripts/dahlia_addresses.json', 'w'))
