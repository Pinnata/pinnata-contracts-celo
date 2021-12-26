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

  sub_addr = addr.get('mainnet')

  celo = interface.IERC20(sub_addr.get('celo'))

  core_oracle = CoreOracle.at(sub_addr.get('core_oracle'))
  proxy_oracle = ProxyOracle.at(sub_addr.get('proxy_oracle'))
  sorted_oracle = CeloProxyPriceProvider.at(sub_addr.get('sorted_oracle'))

  core_oracle.setRoute([
    celo
  ], [
    sorted_oracle
  ], {'from': deployer})

  proxy_oracle.setTokenFactors([
    celo
  ], [
    [13000, 7800, 10250]
  ], {'from': deployer})
