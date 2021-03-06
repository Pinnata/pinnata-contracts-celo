from brownie import (
    accounts,
    WStakingRewards, 
    ProxyOracle,
    interface,
    network
)

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
    ube_factory = interface.IUniswapV2Factory(mainnet_addr.get('ube_factory'))
    proxy_oracle = ProxyOracle.at(mainnet_addr.get('proxy_oracle'))

    celo_ube_lp = ube_factory.getPair(celo, ube)
    celo_mcusd_lp = ube_factory.getPair(celo, mcusd)
    celo_mceur_lp = ube_factory.getPair(celo, mceur)
    celo_scelo_lp = ube_factory.getPair(celo, scelo)
    mcusd_mceur_lp = ube_factory.getPair(mcusd, mceur)

    celo_ube_wstaking = WStakingRewards.deploy(
        mainnet_addr.get('ube_celo_staking'),
        celo_ube_lp,
        ube,
        {'from': deployer}
    )
    celo_mcusd_wstaking = WStakingRewards.deploy(
        mainnet_addr.get('celo_mcusd_staking'),
        celo_mcusd_lp,
        ube,
        {'from': deployer}
    )
    celo_mceur_wstaking = WStakingRewards.deploy(
        mainnet_addr.get('celo_mceur_staking'),
        celo_mceur_lp,
        ube,
        {'from': deployer}
    )
    celo_scelo_wstaking = WStakingRewards.deploy(
        mainnet_addr.get('celo_scelo_staking'),
        celo_scelo_lp,
        ube,
        {'from': deployer}
    )
    mcusd_mceur_wstaking = WStakingRewards.deploy(
        mainnet_addr.get('mcusd_mceur_staking'),
        mcusd_mceur_lp,
        ube,
        {'from': deployer}
    )

    proxy_oracle.setWhitelistERC1155(
        [celo_ube_wstaking, celo_mcusd_wstaking, celo_mceur_wstaking, celo_scelo_wstaking, mcusd_mceur_wstaking],
        True,
        {'from': deployer},
    )

    addr.get('mainnet').update({
        'celo_ube_wstaking': celo_ube_wstaking.address,
        'celo_mcusd_wstaking': celo_mcusd_wstaking.address,
        'celo_mceur_wstaking': celo_mceur_wstaking.address, 
        'celo_scelo_wstaking': celo_scelo_wstaking.address,
        'mcusd_mceur_wstaking': mcusd_mceur_wstaking.address,
    })

    print(json.dumps(addr, indent=4), file=open('scripts/dahlia_addresses.json', 'w'))