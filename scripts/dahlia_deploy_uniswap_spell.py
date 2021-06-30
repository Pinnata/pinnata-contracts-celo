from brownie import (
    accounts, HomoraBank, UniswapV2SpellV1, WERC20,
)
from brownie import interface
from .utils import *
import json

def main():
    deployer = accounts.load('gh')
    f = open('scripts/dahlia_addresses.json')
    addr = json.load(f)['alfajores']

    celo = interface.IERC20Ex(addr['celo'])
    ube = interface.IERC20Ex(addr['ube'])
    btc = interface.IERC20Ex(addr['btc'])
    mcusd = interface.IERC20Ex(addr['mcusd'])
    mceur = interface.IERC20Ex(addr['mceur'])
    scelo = interface.IERC20Ex(addr['scelo'])
    ube_router = interface.IUniswapV2Router02(addr['ube'])
    werc20 = WERC20.at(addr['werc20'])
    dahlia_bank = HomoraBank.at(addr['dahlia_bank'])

    uniswap_spell = UniswapV2SpellV1.deploy(
        dahlia_bank, werc20, ube_router, celo,
        {'from': deployer},
    )

    uniswap_spell.getAndApprovePair(celo, ube, {'from': deployer})
    uniswap_spell.getAndApprovePair(mcusd, btc, {'from': deployer})
    uniswap_spell.getAndApprovePair(celo, mcusd, {'from': deployer})
    uniswap_spell.getAndApprovePair(scelo, celo, {'from': deployer})
    uniswap_spell.getAndApprovePair(celo, mceur, {'from': deployer})

    ube_factory_address = ube_router.factory()
    ube_factory = interface.IUniswapV2Factory(ube_factory_address)
    celo_ube_lp = ube_factory.getPair(celo, ube)
    mcusd_btc_lp = ube_factory.getPair(mcusd, btc)
    celo_mcusd_lp = ube_factory.getPair(celo, mcusd)
    scelo_celo_lp = ube_factory.getPair(scelo, celo)
    celo_mceur_lp = ube_factory.getPair(celo, mceur)

    uniswap_spell.setWhitelistLPTokens([celo_ube_lp, mcusd_btc_lp, celo_mcusd_lp, scelo_celo_lp, celo_mceur_lp], [True, True, True, True, True], {'from': deployer})

    dahlia_bank.setWhitelistSpells([uniswap_spell], [True], {'from': deployer})

    print('Done!')
