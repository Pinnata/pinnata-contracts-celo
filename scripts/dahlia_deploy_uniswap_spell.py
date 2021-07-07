from brownie import (
    accounts, HomoraBank, UniswapV2SpellV1, WERC20,
)
from brownie import interface
from .utils import *
import json

def main():
    deployer = accounts.load('admin')
    f = open('scripts/dahlia_addresses.json')
    addr = json.load(f)['mainnet']

    celo = interface.IERC20Ex(addr['celo'])
    btc = interface.IERC20Ex(addr['btc'])
    ube = interface.IERC20Ex(addr['ube'])
    mcusd = interface.IERC20Ex(addr['mcusd'])
    mceur = interface.IERC20Ex(addr['mceur'])
    scelo = interface.IERC20Ex(addr['scelo'])
    ube_router = interface.IUniswapV2Router02(addr['ube_router'])
    ube_factory = interface.IUniswapV2Factory(addr['ube_factory'])
    werc20 = WERC20.at(addr['werc20'])
    dahlia_bank = HomoraBank.at(addr['dahlia_bank'])

    uniswap_spell = UniswapV2SpellV1.deploy(
        dahlia_bank, werc20, ube_router, celo,
        {'from': deployer},
    )

    uniswap_spell.getAndApprovePair(celo, ube, {'from': deployer})
    # uniswap_spell.getAndApprovePair(mcusd, btc, {'from': deployer})
    uniswap_spell.getAndApprovePair(celo, mcusd, {'from': deployer})
    uniswap_spell.getAndApprovePair(scelo, celo, {'from': deployer})
    uniswap_spell.getAndApprovePair(celo, mceur, {'from': deployer})

    celo_ube_lp = ube_factory.getPair(celo, ube)
    # mcusd_btc_lp = ube_factory.getPair(mcusd, btc)
    celo_mcusd_lp = ube_factory.getPair(celo, mcusd)
    celo_mceur_lp = ube_factory.getPair(celo, mceur)
    scelo_celo_lp = ube_factory.getPair(scelo, celo)

    uniswap_spell.setWhitelistLPTokens([celo_ube_lp], [True], {'from': deployer})
    uniswap_spell.setWhitelistLPTokens([celo_mcusd_lp], [True], {'from': deployer})
    uniswap_spell.setWhitelistLPTokens([scelo_celo_lp], [True], {'from': deployer})
    # uniswap_spell.setWhitelistLPTokens([mcusd_btc_lp], [True], {'from': deployer})
    uniswap_spell.setWhitelistLPTokens([celo_mceur_lp], [True], {'from': deployer})


    dahlia_bank.setWhitelistSpells([uniswap_spell], [True], {'from': deployer})

    print('Done!')
