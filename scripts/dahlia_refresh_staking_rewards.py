from brownie import (
    accounts,
    interface,
    network,
    MockERC20,
    MockStakingRewards,
    MockMoolaStakingRewards,
    WMStakingRewards,
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
    mock = interface.IERC20Ex(alfajores_addr.get('mock'))
    mock2 = interface.IERC20Ex(alfajores_addr.get('mock2'))

    celo_cusd_staking = MockStakingRewards.at(alfajores_addr.get('celo_cusd_staking'))
    celo_ceur_staking = MockStakingRewards.at(alfajores_addr.get('celo_ceur_staking'))
    cusd_ceur_staking = MockStakingRewards.at(alfajores_addr.get('cusd_ceur_staking'))

    celo_cusd_mstaking = MockMoolaStakingRewards.at(alfajores_addr.get('celo_cusd_mstaking'))
    celo_ceur_mstaking = MockMoolaStakingRewards.at(alfajores_addr.get('celo_ceur_mstaking'))
    cusd_ceur_mstaking = MockMoolaStakingRewards.at(alfajores_addr.get('cusd_ceur_mstaking'))

    ufactory = interface.IUniswapV2Factory(alfajores_addr.get('ufactory'))

    celo_cusd_lp = ufactory.getPair(celo, cusd)
    celo_ceur_lp = ufactory.getPair(celo, ceur)
    cusd_ceur_lp = ufactory.getPair(cusd, ceur)

    mock.mint(celo_cusd_staking, 1000*10**18, {'from': deployer})
    mock.mint(celo_ceur_staking, 1000*10**18, {'from': deployer})
    mock.mint(cusd_ceur_staking, 1000*10**18, {'from': deployer})

    celo_cusd_staking.setRewardsDuration(60*60*24*7, {'from': deployer})
    celo_ceur_staking.setRewardsDuration(60*60*24*7, {'from': deployer})
    cusd_ceur_staking.setRewardsDuration(60*60*24*7, {'from': deployer})

    celo_cusd_staking.notifyRewardAmount(500*10**18, {'from': deployer})
    celo_ceur_staking.notifyRewardAmount(500*10**18, {'from': deployer})
    cusd_ceur_staking.notifyRewardAmount(500*10**18, {'from': deployer})

    mock2.mint(celo_cusd_mstaking, 1000*10**18, {'from': deployer})
    mock2.mint(celo_ceur_mstaking, 1000*10**18, {'from': deployer})
    mock2.mint(cusd_ceur_mstaking, 1000*10**18, {'from': deployer})

    celo_cusd_mstaking.setRewardsDuration(60*60*24*7, {'from': deployer})
    celo_ceur_mstaking.setRewardsDuration(60*60*24*7, {'from': deployer})
    cusd_ceur_mstaking.setRewardsDuration(60*60*24*7, {'from': deployer})

    celo_cusd_mstaking.notifyRewardAmount(500*10**18, {'from': deployer})
    celo_ceur_mstaking.notifyRewardAmount(500*10**18, {'from': deployer})
    cusd_ceur_mstaking.notifyRewardAmount(500*10**18, {'from': deployer})