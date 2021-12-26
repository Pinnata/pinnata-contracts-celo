from brownie import (
    DiaAdapterOracle,
    accounts,
    network,
    interface,
    UniswapV2Oracle,
    ProxyOracle,
    CoreOracle,
)
import json

network.gas_limit(8000000)

def main():
  deployer = accounts.load('dahlia_admin')

  with open('scripts/dahlia_addresses.json', 'r') as f:
    addr = json.load(f)
  sub_addr = addr.get('mainnet')

  celo = sub_addr.get('celo')
  ube = sub_addr.get('ube')
  mobi = sub_addr.get('mobi')
  wbtc = sub_addr.get('wbtc')
  weth = sub_addr.get('weth')
  dia_address = sub_addr.get('dia_oracle')

  dia_oracle = DiaAdapterOracle.deploy(dia_address, 180, {'from': deployer})
  
  dia_oracle.setQuery(ube, 'UBE/USD', {'from': deployer})
  dia_oracle.setQuery(mobi, 'MOBI/USD', {'from': deployer})
  dia_oracle.setQuery(wbtc, 'WBTC/USD', {'from': deployer})
  dia_oracle.setQuery(weth, 'ETH/USD', {'from': deployer})

  core_oracle = CoreOracle.at(sub_addr.get('core_oracle'))
  proxy_oracle = ProxyOracle.at(sub_addr.get('proxy_oracle'))

  ubeswap_factory = interface.IUniswapV2Factory(sub_addr.get('ube_factory'))

  sushi_oracle = UniswapV2Oracle.at(sub_addr.get('sushi_oracle'))

  celo_mobi_lp = ubeswap_factory.getPair(celo, mobi)
  celo_ube_lp = ubeswap_factory.getPair(celo, ube)

  core_oracle.setRoute([
      ube,
      mobi,
      celo_mobi_lp,
      celo_ube_lp,
  ], [
      dia_oracle, 
      dia_oracle,
      sushi_oracle,
      sushi_oracle
  ], {'from': deployer})

  proxy_oracle.setTokenFactors([
      ube,
      mobi,
      celo_mobi_lp,
      celo_ube_lp,
  ], [
      [13000, 7800, 10250],
      [13000, 7800, 10250],
      [50000, 7800, 10250],
      [50000, 7800, 10250]
  ], {'from': deployer})


  addr.get('mainnet').update({
      'dia_adapter': dia_oracle.address,
  })

  print(json.dumps(addr, indent=4), file=open('scripts/dahlia_addresses.json', 'w'))
