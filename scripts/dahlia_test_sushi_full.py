from brownie import (
    accounts,
    WComplexTimeRewarder, 
    ProxyOracle,
    interface,
    network,
    WERC20,
    Contract,
    SushiswapSpellV1,
    HomoraBank,
    WMiniChefV2,
    ProxyOracle,
)

import json

network.gas_limit(8000000)

def main():
    deployer = accounts.load('dahlia_admin')
    alice = accounts.load('dahlia_alice')

    with open('scripts/dahlia_addresses.json', 'r') as f:
        addr = json.load(f)
    mainnet_addr = addr.get('mainnet')

    celo = interface.IERC20Ex(mainnet_addr['celo'])
    cusd = interface.IERC20Ex(mainnet_addr['cusd'])
    ceur = interface.IERC20Ex(mainnet_addr['ceur'])
    dahlia_bank = Contract.from_abi("HomoraBank", mainnet_addr.get('dahlia_bank'), HomoraBank.abi)
    sushi_spell = SushiswapSpellV1.at(mainnet_addr['sushi_spell'])
    sushi = interface.IERC20Ex(mainnet_addr['sushi'])
    proxy_oracle = ProxyOracle.at(mainnet_addr.get('proxy_oracle'))
    minichef = mainnet_addr.get('minichef')
    sushi_router = interface.IUniswapV2Router02(mainnet_addr.get('sushi_router'))
    sushi_factory = interface.IUniswapV2Factory(mainnet_addr.get('sushi_factory'))

    wminichef = WMiniChefV2.deploy(
        minichef,
        {'from': deployer}
    )

    proxy_oracle.setWhitelistERC1155(
        [wminichef],
        True,
        {'from': deployer},
    )

    werc20 = WERC20.at(mainnet_addr.get('werc20'))
    dahlia_bank = Contract.from_abi("HomoraBank", mainnet_addr.get('dahlia_bank'), HomoraBank.abi)

    sushi_spell = SushiswapSpellV1.deploy(
        dahlia_bank, werc20, sushi_router, wminichef, celo, celo,
        {'from': deployer},
    )

    sushi_spell.getAndApprovePair(cusd, ceur, {'from': deployer})

    cusd_ceur_lp = sushi_factory.getPair(cusd, ceur)

    sushi_spell.setWhitelistLPTokens([cusd_ceur_lp], [True], {'from': deployer})

    dahlia_bank.setWhitelistSpells([sushi_spell], [True], {'from': deployer})

    rewarder = mainnet_addr.get('sushi_rewarder')

    wrewarder = WComplexTimeRewarder.deploy(rewarder, celo, {'from': deployer})

    wminichef.set(3, wrewarder, {'from': deployer})

    dahlia_bank.execute(
        0,
        sushi_spell,
        sushi_spell.addLiquidityWMiniChef.encode_input(
            cusd,
            ceur,
            [
             10**15,
             10**15,
             0,
             10**15,
             10**15,
             0,
             0,
             0
            ],
            3
        ),
        {
            'from': alice, 
        }
    )
