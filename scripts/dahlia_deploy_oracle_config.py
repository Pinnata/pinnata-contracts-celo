from brownie import (
    accounts,
    network,
    interface,
    UniswapV2Oracle,
    ProxyOracle,
    CoreOracle,
    SimpleOracle,
    WERC20,
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
    core_oracle = CoreOracle.at(alfajores_addr.get('core_oracle'))
    proxy_oracle = ProxyOracle.at(alfajores_addr.get('proxy_oracle'))
    ufactory = interface.IUniswapV2Factory(alfajores_addr.get('ufactory'))

    uni_oracle = UniswapV2Oracle.deploy(core_oracle, {'from': deployer})
    simple_oracle = SimpleOracle.deploy({'from': deployer})

    simple_oracle.setCELOPx([celo, cusd, ceur], [2**112, 2**112 / 6, 2**112 / 5])

    celo_cusd_lp = ufactory.getPair(celo, cusd)
    celo_ceur_lp = ufactory.getPair(celo, ceur)
    cusd_ceur_lp = ufactory.getPair(cusd, ceur)

    core_oracle.setRoute([
        celo,
        cusd,
        ceur,
        celo_cusd_lp,
        celo_ceur_lp,
        cusd_ceur_lp,
    ], [
        simple_oracle, 
        simple_oracle, 
        simple_oracle,
        uni_oracle,
        uni_oracle,
        uni_oracle,
    ], {'from': deployer})

    proxy_oracle.setTokenFactors([
        celo,
        cusd,
        ceur,
        celo_cusd_lp,
        celo_ceur_lp,
        cusd_ceur_lp,
    ], [
        [13000, 7800, 10250],
        [11000, 9000, 10250],
        [11000, 9000, 10250],
        [50000, 7800, 10250],
        [50000, 7800, 10250],
        [50000, 7800, 10250],
    ], {'from': deployer})

    werc20 = WERC20.deploy({'from': deployer})

    proxy_oracle.setWhitelistERC1155(
        [werc20],
        True,
        {'from': deployer},
    )

    addr.get('alfajores').update({
        'uni_oracle': uni_oracle.address,
        'simple_oracle': simple_oracle.address,
        'werc20': werc20.address,
    })

    print(json.dumps(addr, indent=4), file=open('scripts/dahlia_addresses.json', 'w'))