from brownie import (
    accounts, UbeswapV1Oracle, network
)
import json
import time
import argparse

network.gas_limit(8000000)


def main():
  parser = argparse.ArgumentParser(description='Process some integers.')
  parser.add_argument('--type', action="store_true", default="prod")
  args = parser.parse_args()
  print(network)
  print(args.type)
  # deployer = accounts.load('dahlia_admin')
  # with open('scripts/dahlia_addresses.json', 'r') as f:
  #     addr = json.load(f)


  # mainnet_addr = addr.get('mainnet')

  # ubeswap_oracle = UbeswapV1Oracle.at(mainnet_addr.get('ube_oracle'))

  # while True:
  #     if ubeswap_oracle.workable():
  #         ubeswap_oracle.work({'from': deployer})
  #         print("work")
  #     else:
  #         print("no work")
          
  #     time.sleep(60)