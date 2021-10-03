from brownie import (
    accounts,
    interface,
    network,
    MockERC20,
    MockStakingRewards,
    WStakingRewards,
    ProxyOracle,
)
import json

network.gas_limit(8000000)

def main():
    deployer = accounts.load('dahlia_admin')

    with open('scripts/dahlia_addresses.json', 'r') as f:
        addr = json.load(f)

    alfajores_addr = addr.get('alfajores')

    celo = interface.IERC20Ex(alfajores_addr.get('celo'))
    cusd = interface.IERC20Ex(alfajores_addr.get('cusd'))
    ceur = interface.IERC20Ex(alfajores_addr.get('ceur'))
    ufactory = interface.IUniswapV2Factory(alfajores_addr.get('ufactory'))
    proxy_oracle = ProxyOracle.at(alfajores_addr.get('proxy_oracle'))

    celo_cusd_lp = ufactory.getPair(celo, cusd)
    celo_ceur_lp = ufactory.getPair(celo, ceur)
    cusd_ceur_lp = ufactory.getPair(cusd, ceur)

    mock = MockERC20.deploy('Dahlia Token', 'GROW', 18, {'from': deployer})

    celo_cusd_staking = MockStakingRewards.deploy(deployer, deployer, mock, celo_cusd_lp, {'from': deployer})
    celo_ceur_staking = MockStakingRewards.deploy(deployer, deployer, mock, celo_ceur_lp, {'from': deployer})
    cusd_ceur_staking = MockStakingRewards.deploy(deployer, deployer, mock, cusd_ceur_lp, {'from': deployer})

    mock.mint(celo_cusd_staking, 1000*10**18, {'from': deployer})
    mock.mint(celo_ceur_staking, 1000*10**18, {'from': deployer})
    mock.mint(cusd_ceur_staking, 1000*10**18, {'from': deployer})

    celo_cusd_staking.setRewardsDuration(60*60*24*7, {'from': deployer})
    celo_ceur_staking.setRewardsDuration(60*60*24*7, {'from': deployer})
    cusd_ceur_staking.setRewardsDuration(60*60*24*7, {'from': deployer})

    celo_cusd_staking.notifyRewardAmount(500*10**18, {'from': deployer})
    celo_ceur_staking.notifyRewardAmount(500*10**18, {'from': deployer})
    cusd_ceur_staking.notifyRewardAmount(500*10**18, {'from': deployer})

    celo_cusd_wstaking = WStakingRewards.deploy(
        celo_cusd_staking,
        celo_cusd_lp,
        mock,
        {'from': deployer}
    )

    celo_ceur_wstaking = WStakingRewards.deploy(
        celo_ceur_staking,
        celo_ceur_lp,
        mock,
        {'from': deployer}
    )

    cusd_ceur_wstaking = WStakingRewards.deploy(
        cusd_ceur_staking,
        cusd_ceur_lp,
        mock,
        {'from': deployer}
    )

    proxy_oracle.setWhitelistERC1155(
        [celo_cusd_wstaking, celo_ceur_wstaking, cusd_ceur_wstaking],
        True,
        {'from': deployer},
    )

    addr.get('alfajores').update({
        'mock': mock.address,
        'celo_cusd_staking': celo_cusd_staking.address,
        'celo_ceur_staking': celo_ceur_staking.address,
        'cusd_ceur_staking': cusd_ceur_staking.address,
        'celo_cusd_wstaking': celo_cusd_wstaking.address,
        'celo_ceur_wstaking': celo_ceur_wstaking.address,
        'cusd_ceur_wstaking': cusd_ceur_wstaking.address,
    })

    print(json.dumps(addr, indent=4), file=open('scripts/dahlia_addresses.json', 'w'))