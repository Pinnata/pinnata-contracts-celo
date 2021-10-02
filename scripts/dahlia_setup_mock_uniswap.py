from brownie import (
    accounts,
    interface,
    network,
    MockUniswapV2Factory,
    MockUniswapV2Router02,
)
import json

network.gas_limit(8000000)

def main():
    deployer = accounts.load('dahlia_admin')
    alice = accounts.load('dahlia_alice')

    with open('scripts/dahlia_addresses.json', 'r') as f:
        addr = json.load(f)

    alfajores_addr = addr.get('alfajores')

    celo = interface.IERC20Ex(alfajores_addr.get('celo'))
    cusd = interface.IERC20Ex(alfajores_addr.get('cusd'))
    ceur = interface.IERC20Ex(alfajores_addr.get('ceur'))

    ufactory = MockUniswapV2Factory.deploy(deployer, {'from': deployer})

    urouter = MockUniswapV2Router02.deploy(ufactory, {'from': deployer})

    celo.approve(urouter, 2**256-1, {'from': alice})
    cusd.approve(urouter, 2**256-1, {'from': alice})
    ceur.approve(urouter, 2**256-1, {'from': alice})

    urouter.addLiquidity(
        celo,
        cusd,
        2 * 10**18,
        12 * 10**18,
        0,
        0,
        alice,
        2**256-1,
        {'from': alice},
    )

    urouter.addLiquidity(
        celo,
        ceur,
        2 * 10**18,
        10 * 10**18,
        0,
        0,
        alice,
        2**256-1,
        {'from': alice},
    )

    urouter.addLiquidity(
        cusd,
        ceur,
        10 * 10**18,
        8 * 10**18,
        0,
        0,
        alice,
        2**256-1,
        {'from': alice},
    )

    addr.get('alfajores').update({
        'ufactory': ufactory.address,
        'urouter': urouter.address,
    })

    print(json.dumps(addr, indent=4), file=open('scripts/dahlia_addresses.json', 'w'))