from brownie import (
    accounts,
    WMStakingRewards, 
    ProxyOracle,
    interface,
    network,
)

import json

network.gas_limit(8000000)

def main():
    deployer = accounts.load('dahlia_admin')

    with open('scripts/dahlia_addresses.json', 'r') as f:
        addr = json.load(f)
    mainnet_addr = addr.get('mainnet')

    mcusd = interface.IERC20Ex(mainnet_addr.get('mcusd'))
    mceur = interface.IERC20Ex(mainnet_addr.get('mceur'))
    celo = interface.IERC20Ex(mainnet_addr.get('celo'))
    ube = mainnet_addr.get('ube')
    moo = mainnet_addr.get('moo')
    ube_factory = interface.IUniswapV2Factory(mainnet_addr.get('ube_factory'))
    proxy_oracle = ProxyOracle.at(mainnet_addr.get('proxy_oracle'))
    celo_mcusd_mstaking = mainnet_addr.get('celo_mcusd_mstaking')
    celo_mceur_mstaking = mainnet_addr.get('celo_mceur_mstaking')
    mcusd_mceur_mstaking = mainnet_addr.get('mcusd_mceur_mstaking')

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
        [celo_mcusd_wmstaking, celo_mceur_wmstaking, mcusd_mceur_wmstaking],
        True,
        {'from': deployer},
    )
    
    addr.get('mainnet').update({
        'celo_mcusd_wmstaking': celo_mcusd_wmstaking.address,
        'celo_mceur_wmstaking': celo_mceur_wmstaking.address,
        'mcusd_mceur_wmstaking': mcusd_mceur_wmstaking.address,
    })

    print(json.dumps(addr, indent=4), file=open('scripts/dahlia_addresses.json', 'w'))
