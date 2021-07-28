from brownie import (
    accounts, HomoraBank, SushiswapSpellV1, WERC20,
)
from brownie import interface
from .utils import *
import json

def main():
    deployer = accounts.load('admin')
    f = open('scripts/dahlia_addresses.json')
    addr = json.load(f)['mainnet']

    celo = interface.IERC20Ex(addr['celo'])
    cusd = interface.IERC20Ex(addr['cusd'])
    ceur = interface.IERC20Ex(addr['ceur'])
    mzpn = interface.IERC20Ex(addr['mzpn'])
    ube_router = interface.IUniswapV2Router02(addr['ube_router'])
    ube_factory = interface.IUniswapV2Factory(addr['ube_factory'])
    werc20 = WERC20.at(addr['werc20'])
    dahlia_bank = HomoraBank.at(addr['dahlia_bank'])

    sushiswap_spell = SushiswapSpellV1.deploy(
        dahlia_bank, werc20, ube_router, addr['marzipan_masterchef'], celo,
        {'from': deployer},
    )

    sushiswap_spell.getAndApprovePair(celo, mzpn, {'from': deployer})
    sushiswap_spell.getAndApprovePair(cusd, mzpn, {'from': deployer})
    sushiswap_spell.getAndApprovePair(ceur, mzpn, {'from': deployer})
    sushiswap_spell.getAndApprovePair(celo, cusd, {'from': deployer})

    celo_mzpn_lp = ube_factory.getPair(celo, mzpn)
    cusd_mzpn_lp = ube_factory.getPair(cusd, mzpn)
    ceur_mzpn_lp = ube_factory.getPair(ceur, mzpn)
    celo_cusd_lp = ube_factory.getPair(celo, cusd)

    sushiswap_spell.setWhitelistLPTokens([celo_mzpn_lp], [True], {'from': deployer})
    sushiswap_spell.setWhitelistLPTokens([cusd_mzpn_lp], [True], {'from': deployer})
    sushiswap_spell.setWhitelistLPTokens([ceur_mzpn_lp], [True], {'from': deployer})
    sushiswap_spell.setWhitelistLPTokens([celo_cusd_lp], [True], {'from': deployer})


    dahlia_bank.setWhitelistSpells([sushiswap_spell], [True], {'from': deployer})

    print('Done!')
