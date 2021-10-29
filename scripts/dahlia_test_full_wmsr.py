from brownie import (
    accounts,
    WMStakingRewards, 
    ProxyOracle,
    interface,
    network,
    WERC20,
    Contract,
    UbeswapMSRSpellV1,
    HomoraBank,
)

import json

network.gas_limit(8000000)

def lend(bob, token, safebox):
    token.approve(safebox, 2**256-1, {'from': bob})

    bob_amt = 10**16
    safebox.deposit(bob_amt, {'from': bob})

def main():
    deployer = accounts.load('dahlia_admin')
    alice = accounts.load('dahlia_alice')
    # bob = accounts.load('dahlia_bob')

    with open('scripts/dahlia_addresses.json', 'r') as f:
        addr = json.load(f)
    mainnet_addr = addr.get('mainnet')

    mcusd = interface.IERC20Ex(mainnet_addr.get('mcusd'))
    mceur = interface.IERC20Ex(mainnet_addr.get('mceur'))
    celo = interface.IERC20Ex(mainnet_addr.get('celo'))
    ube = mainnet_addr.get('ube')
    moo = mainnet_addr.get('moo')
    ube_factory = interface.IUniswapV2Factory(mainnet_addr.get('ube_factory'))
    ube_router = interface.IUniswapV2Router02(mainnet_addr.get('ube_router'))
    proxy_oracle = ProxyOracle.at(mainnet_addr.get('proxy_oracle'))
    celo_mcusd_mstaking = mainnet_addr.get('celo_mcusd_mstaking')
    celo_mceur_mstaking = mainnet_addr.get('celo_mceur_mstaking')
    mcusd_mceur_mstaking = mainnet_addr.get('mcusd_mceur_mstaking')

    werc20 = WERC20.at(mainnet_addr.get('werc20'))
    dahlia_bank = Contract.from_abi("HomoraBank", mainnet_addr.get('dahlia_bank'), HomoraBank.abi)

    celo_mcusd_lp = ube_factory.getPair(celo, mcusd)
    celo_mceur_lp = ube_factory.getPair(celo, mceur)
    mcusd_mceur_lp = ube_factory.getPair(mcusd, mceur)

    celo_mcusd_wmstaking = WMStakingRewards.deploy(
        celo_mcusd_mstaking,
        celo_mcusd_lp,
        [celo, ube],
        2,
        {'from': deployer}
    )

    celo_mceur_wmstaking = WMStakingRewards.deploy(
        celo_mceur_mstaking,
        celo_mceur_lp,
        [celo, ube],
        2,
        {'from': deployer}
    )

    mcusd_mceur_wmstaking = WMStakingRewards.deploy(
        mcusd_mceur_mstaking,
        mcusd_mceur_lp,
        [celo, ube, moo],
        3,
        {'from': deployer}
    )

    proxy_oracle.setWhitelistERC1155(
        [celo_mceur_wmstaking, mcusd_mceur_wmstaking],
        True,
        {'from': deployer},
    )

    ubeswap_spell = UbeswapMSRSpellV1.deploy(
        dahlia_bank, werc20, ube_router, celo,
        {'from': deployer},
    )

    ubeswap_spell.getAndApprovePair(celo, mcusd, {'from': deployer})
    ubeswap_spell.getAndApprovePair(celo, mceur, {'from': deployer})
    ubeswap_spell.getAndApprovePair(mcusd, mceur, {'from': deployer})

    ubeswap_spell.setWhitelistLPTokens([celo_mceur_lp, mcusd_mceur_lp], [True, True], {'from': deployer})

    dahlia_bank.setWhitelistSpells([ubeswap_spell], [True], {'from': deployer})

    celo.approve(dahlia_bank, 2**256-1, {'from': alice})
    mcusd.approve(dahlia_bank, 2**256-1, {'from': alice})

    celo.approve(dahlia_bank, 2**256-1, {'from': bob})
    mcusd.approve(dahlia_bank, 2**256-1, {'from': bob})

    # open a position
    dahlia_bank.execute(
        0,
        ubeswap_spell,
        ubeswap_spell.addLiquidityWStakingRewards.encode_input(
            mcusd,
            celo,
            [
             6*10**14,
             10**14,
             0,
             0,
             0,
             0,
             0,
             0
            ],
            celo_mcusd_wmstaking
        ),
        {
            'from': alice, 
        }
    )
    
    addr.get('mainnet').update({
        # 'celo_mcusd_wmstaking': celo_mcusd_wmstaking.address,
        'celo_mceur_wmstaking': celo_mceur_wmstaking.address,
        'mcusd_mceur_wmstaking': mcusd_mceur_wmstaking.address,
    })

    print(json.dumps(addr, indent=4), file=open('scripts/dahlia_addresses.json', 'w'))
