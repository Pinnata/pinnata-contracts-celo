from brownie import (
    accounts, ERC20KP3ROracle, UniswapV2Oracle, ProxyOracle, CoreOracle,
    WERC20, UbeswapV1Oracle
)
from brownie import interface
import json

def main():
    deployer = accounts.load('dahlia_admin')

    with open('scripts/dahlia_addresses.json', 'r') as f:
        addr = json.load(f)

    mainnet_addr = addr.get('mainnet')
    core_oracle = CoreOracle.at(mainnet_addr.get('core_oracle'))
    proxy_oracle = ProxyOracle.at(mainnet_addr.get('proxy_oracle'))
    celo = interface.IERC20Ex(mainnet_addr.get('celo'))
    mcusd = interface.IERC20Ex(mainnet_addr.get('mcusd'))
    mceur = interface.IERC20Ex(mainnet_addr.get('mceur'))
    ube = interface.IERC20Ex(mainnet_addr.get('ube'))
    scelo = interface.IERC20Ex(mainnet_addr.get('scelo'))
    ube_router = interface.IUniswapV2Router02(mainnet_addr.get('ube_router'))

    uni_oracle = UniswapV2Oracle.deploy(core_oracle, {'from': deployer})
    ube_oracle = UbeswapV1Oracle.deploy({'from': deployer})

    ube_oracle.addPair(celo, ube, {'from': deployer})
    ube_oracle.addPair(celo, mcusd, {'from': deployer})
    ube_oracle.addPair(celo, mceur, {'from': deployer})
    ube_oracle.addPair(celo, scelo, {'from': deployer})

    kp3r_oracle = ERC20KP3ROracle.deploy(ube_oracle, {'from': deployer})

    ube_factory_address = ube_router.factory({'from': deployer})
    ube_factory = interface.IUniswapV2Factory(ube_factory_address)

    celo_ube_lp = ube_factory.getPair(celo, ube)
    celo_mcusd_lp = ube_factory.getPair(celo, mcusd)
    celo_mceur_lp = ube_factory.getPair(celo, mceur)
    celo_scelo_lp = ube_factory.getPair(celo, scelo)
    mcusd_mceur_lp = ube_factory.getPair(mcusd, mceur)

    core_oracle.setRoute([
        celo,
        mcusd, 
        mceur,
        ube,
        scelo,
        celo_ube_lp,
        celo_mcusd_lp,
        celo_mceur_lp,
        celo_scelo_lp,
        mcusd_mceur_lp
    ], [
        kp3r_oracle,
        kp3r_oracle,
        kp3r_oracle,
        kp3r_oracle,
        kp3r_oracle,
        uni_oracle,
        uni_oracle,
        uni_oracle,
        uni_oracle,
        uni_oracle,
    ], {'from': deployer})

    proxy_oracle.setTokenFactors([
        celo,
        mcusd, 
        mceur,
        ube,
        scelo,
        celo_ube_lp,
        celo_mcusd_lp,
        celo_mceur_lp,
        celo_scelo_lp,
        mcusd_mceur_lp
    ], [
        [13000, 7800, 10250],
        [11000, 9000, 10250],
        [11000, 9000, 10250],
        [13000, 7800, 10250],
        [13000, 7800, 10250],
        [50000, 7800, 10250],
        [50000, 7800, 10250],
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
        'ube_oracle': ube_oracle.address,
        'kp3r_oracle': kp3r_oracle.address, 
        'werc20': werc20.address,
    })

    print(json.dumps(addr, indent=4), file=open('scripts/dahlia_addresses.json', 'w'))