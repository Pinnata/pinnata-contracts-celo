from brownie import (
    accounts,
    interface,
    network,
    MockMoolaStakingRewards,
    WMStakingRewards,
    ProxyOracle,
)
import json

network.gas_limit(8000000)

zero_add = '0x0000000000000000000000000000000000000000'

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
    celo_cusd_mstaking = MockMoolaStakingRewards.at(alfajores_addr.get('celo_cusd_mstaking'))
    celo_ceur_mstaking = MockMoolaStakingRewards.at(alfajores_addr.get('celo_ceur_mstaking'))
    cusd_ceur_mstaking = MockMoolaStakingRewards.at(alfajores_addr.get('cusd_ceur_mstaking'))
    ufactory = interface.IUniswapV2Factory(alfajores_addr.get('ufactory'))
    proxy_oracle = ProxyOracle.at(alfajores_addr.get('proxy_oracle'))

    celo_cusd_lp = ufactory.getPair(celo, cusd)
    celo_ceur_lp = ufactory.getPair(celo, ceur)
    cusd_ceur_lp = ufactory.getPair(cusd, ceur)

    celo_cusd_wmstaking = WMStakingRewards.deploy(
        celo_cusd_mstaking,
        celo_cusd_lp,
        [mock2, mock, zero_add, zero_add, zero_add, zero_add, zero_add, zero_add],
        2,
        {'from': deployer}
    )

    celo_ceur_wmstaking = WMStakingRewards.deploy(
        celo_ceur_mstaking,
        celo_ceur_lp,
        [mock2, mock, zero_add, zero_add, zero_add, zero_add, zero_add, zero_add],
        2,
        {'from': deployer}
    )

    cusd_ceur_wmstaking = WMStakingRewards.deploy(
        cusd_ceur_mstaking,
        cusd_ceur_lp,
        [mock2, mock, zero_add, zero_add, zero_add, zero_add, zero_add, zero_add],
        2,
        {'from': deployer}
    )

    proxy_oracle.setWhitelistERC1155(
        [celo_cusd_wmstaking, celo_ceur_wmstaking, cusd_ceur_wmstaking],
        True,
        {'from': deployer},
    )

    addr.get('alfajores').update({
        'celo_cusd_wmstaking': celo_cusd_wmstaking.address,
        'celo_ceur_wmstaking': celo_ceur_wmstaking.address,
        'cusd_ceur_wmstaking': cusd_ceur_wmstaking.address,
    })

    print(json.dumps(addr, indent=4), file=open('scripts/dahlia_addresses.json', 'w'))
