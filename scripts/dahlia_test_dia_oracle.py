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
  addr = json.load(f).get('mainnet')
  ube = addr.get('ube')
  dia_oracle = DiaAdapterOracle.deploy('0x7D1e0D8b0810730e85828EaE1ee1695a95eECf4B', 180, {'from': deployer})
  dia_oracle.setQuery(ube, 'UBE/USD', {'from': deployer})

  print('ube', dia_oracle.getCELOPx(ube))
