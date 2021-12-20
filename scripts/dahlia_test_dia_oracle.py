from brownie import (
    DiaAdapterOracle,
    accounts,
    network,
)
import json

network.gas_limit(8000000)

def main():
  deployer = accounts.load('dahlia_alice')

  f = open('scripts/dahlia_addresses.json')
  addr = json.load(f).get('alpha')

  ube = addr.get('ube')
  mobi = addr.get('mobi')
  wbtc = addr.get('wbtc')
  weth = addr.get('weth')
  dia_address = addr.get('dia_oracle')

  dia_oracle = DiaAdapterOracle.deploy(dia_address, 180, {'from': deployer})
  
  dia_oracle.setQuery(ube, 'UBE/USD', {'from': deployer})
  dia_oracle.setQuery(mobi, 'MOBI/USD', {'from': deployer})
  dia_oracle.setQuery(wbtc, 'WBTC/USD', {'from': deployer})
  dia_oracle.setQuery(weth, 'ETH/USD', {'from': deployer})

  print('ube', float(dia_oracle.getCELOPx(ube)) / 2 ** 112)
  print('mobi', float(dia_oracle.getCELOPx(mobi)) / 2 ** 112)
  print('wbtc', float(dia_oracle.getCELOPx(wbtc)) / 2 ** 112)
  print('weth', float(dia_oracle.getCELOPx(weth)) / 2 ** 112)
