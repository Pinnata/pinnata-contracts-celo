from brownie import (
    accounts,
    network,
    interface,
    UniswapV2Oracle,
    ProxyOracle,
    CoreOracle,
    WERC20,
    CeloProxyPriceProvider,
    MoolaProxyOracle,
)
import json

network.gas_limit(8000000)


def main():
    deployer = accounts.load('dahlia_admin')

    with open('scripts/dahlia_addresses.json', 'r') as f:
        addr = json.load(f)

    mainnet_addr = addr.get('mainnet')

    cusd = interface.IERC20Ex(mainnet_addr.get('cusd'))
    ceur = interface.IERC20Ex(mainnet_addr.get('ceur'))
    core_oracle = CoreOracle.at(mainnet_addr.get('core_oracle'))
    proxy_oracle = ProxyOracle.at(mainnet_addr.get('proxy_oracle'))
    sushi_factory = interface.IUniswapV2Factory(mainnet_addr.get('sushi_factory'))

    sushi_oracle = UniswapV2Oracle.deploy(core_oracle, {'from': deployer})

    sorted_oracle = CeloProxyPriceProvider.deploy({'from': deployer})

    cusd_ceur_lp = sushi_factory.getPair(cusd, ceur)

    core_oracle.setRoute([
        cusd,
        ceur,
        cusd_ceur_lp,
    ], [
        sorted_oracle, 
        sorted_oracle,
        sushi_oracle
    ], {'from': deployer})

    proxy_oracle.setTokenFactors([
        cusd,
        ceur,
        cusd_ceur_lp,
    ], [
        [11000, 9000, 10250],
        [11000, 9000, 10250],
        [50000, 7800, 10250],
    ], {'from': deployer})

    werc20 = WERC20.deploy({'from': deployer})

    proxy_oracle.setWhitelistERC1155(
        [werc20],
        True,
        {'from': deployer},
    )

    addr.get('mainnet').update({
        'sushi_oracle': sushi_oracle.address,
        'sorted_oracle': sorted_oracle.address,
        'werc20': werc20.address,
    })

    print(json.dumps(addr, indent=4), file=open('scripts/dahlia_addresses.json', 'w'))