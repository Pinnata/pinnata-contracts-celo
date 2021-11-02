from brownie import (
    accounts,
    HomoraBank,
    SushiswapSpellV1,
    WERC20,
    Contract,
    network,
    interface,
    WComplexTimeRewarder,
    WMiniChefV2
)
import json

network.gas_limit(8000000)

def main():
    deployer = accounts.load('dahlia_admin')

    with open('scripts/dahlia_addresses.json', 'r') as f:
        addr = json.load(f)
    mainnet_addr = addr.get('mainnet')

    celo = interface.IERC20Ex(mainnet_addr.get('celo'))
    cusd = interface.IERC20Ex(mainnet_addr.get('cusd'))
    ceur = interface.IERC20Ex(mainnet_addr.get('ceur'))
    sushi_router = interface.IUniswapV2Router02(mainnet_addr.get('sushi_router'))
    sushi_factory = interface.IUniswapV2Factory(mainnet_addr.get('sushi_factory'))
    wminichef = WMiniChefV2.at(mainnet_addr.get('wminichef'))
    rewarder = mainnet_addr.get('sushi_rewarder')

    wrewarder = WComplexTimeRewarder.deploy(rewarder, celo, {'from': deployer})
    print(wrewarder.rewardsPerShare(3))

    # wminichef.set(3, wrewarder, {'from': deployer})
    # addr.get('mainnet').update({
    #     'wrewarder': wrewarder.address,
    # })

    print(json.dumps(addr, indent=4), file=open('scripts/dahlia_addresses.json', 'w'))
