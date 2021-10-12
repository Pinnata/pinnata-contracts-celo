from brownie import (
    accounts,
    WMoolaStakingRewards, 
    ProxyOracle,
    interface,
    network
)

import json
import time

network.gas_limit(8000000)


def main():
    deployer = accounts.load('dahlia_admin')
    alice = accounts.load('dahlia_alice')

    with open('scripts/dahlia_addresses.json', 'r') as f:
        addr = json.load(f)
    mainnet_addr = addr.get('mainnet')

    # mcusd = interface.IERC20Ex(mainnet_addr.get('mcusd'))
    # mceur = interface.IERC20Ex(mainnet_addr.get('mceur'))
    celo = interface.IERC20Ex(mainnet_addr.get('celo'))
    ube = interface.IERC20Ex(mainnet_addr.get('ube'))
    ube_factory = interface.IUniswapV2Factory(mainnet_addr.get('ube_factory'))
    proxy_oracle = ProxyOracle.at(mainnet_addr.get('proxy_oracle'))
    celo_ube_lp = interface.IERC20Ex(ube_factory.getPair(celo, ube))
    print(mainnet_addr.get('celo_ube_mstaking'))

    celo_ube_wmstaking = WMoolaStakingRewards.deploy(
        mainnet_addr.get('celo_ube_mstaking'),
        celo_ube_lp,
        celo,
        2,
        {'from': deployer}
    )

    proxy_oracle.setWhitelistERC1155(
        [celo_ube_wmstaking],
        True,
        {'from': deployer},
    )
    

    prevCelo = celo.balanceOf(alice)
    prevUbe = ube.balanceOf(alice)
    # approve
    amount = celo_ube_lp.balanceOf(alice)
    print(amount)
    celo_ube_lp.approve(celo_ube_wmstaking, 2**256-1, {'from': alice})
    celo_ube_wmstaking.mint(amount-1, {'from': alice})
    time.sleep(600)

    celo_ube_wmstaking.burn(10, 2**256-1, {'from': alice})

    postCelo = celo.balanceOf(alice)
    postUbe = ube.balanceOf(alice)

    print(postCelo, prevCelo)
    print(postUbe, prevUbe)

    addr.get('mainnet').update({
        'celo_ube_wmstaking': celo_ube_wmstaking.address
    })

    print(json.dumps(addr, indent=4), file=open('scripts/dahlia_addresses.json', 'w'))