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

    celo = interface.IERC20Ex(mainnet_addr.get('celo'))
    mcusd = interface.IERC20Ex(mainnet_addr.get('mcusd'))
    mceur = interface.IERC20Ex(mainnet_addr.get('mceur'))
    core_oracle = CoreOracle.at(mainnet_addr.get('core_oracle'))
    proxy_oracle = ProxyOracle.at(mainnet_addr.get('proxy_oracle'))
    ufactory = interface.IUniswapV2Factory(mainnet_addr.get('ube_factory'))

    uni_oracle = UniswapV2Oracle.deploy(core_oracle, {'from': deployer})

    sorted_oracle = CeloProxyPriceProvider.deploy({'from': deployer})
    moola_proxy_oracle = MoolaProxyOracle.deploy(sorted_oracle, {'from': deployer})

    celo_mcusd_lp = ufactory.getPair(celo, mcusd)
    celo_mceur_lp = ufactory.getPair(celo, mceur)
    mcusd_mceur_lp = ufactory.getPair(mcusd, mceur)

    core_oracle.setRoute([
        celo,
        mcusd,
        mceur,
        celo_mcusd_lp,
        celo_mceur_lp,
        mcusd_mceur_lp,
    ], [
        sorted_oracle, 
        moola_proxy_oracle, 
        moola_proxy_oracle,
        uni_oracle,
        uni_oracle,
        uni_oracle,
    ], {'from': deployer})

    proxy_oracle.setTokenFactors([
        celo,
        mcusd,
        mceur,
        celo_mcusd_lp,
        celo_mceur_lp,
        mcusd_mceur_lp,
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

    addr.get('mainnet').update({
        'uni_oracle': uni_oracle.address,
        'sorted_oracle': sorted_oracle.address,
        'moola_proxy_oracle': moola_proxy_oracle.address,
        'werc20': werc20.address,
    })

    print(json.dumps(addr, indent=4), file=open('scripts/dahlia_addresses.json', 'w'))