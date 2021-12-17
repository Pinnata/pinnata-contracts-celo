from brownie import (
    interface,
    UniswapV2Oracle,
    CoreOracle
)
import json

def main():
    f = open('scripts/dahlia_addresses.json')
    addr = json.load(f)['alpha']

    mobi = interface.IERC20Ex(addr['mobi'])
    celo = interface.IERC20(addr['celo'])
    core_oracle = CoreOracle.at(addr['core_oracle'])
    sushi_oracle = UniswapV2Oracle.at(addr['sushi_oracle'])
    ube_factory = interface.IUniswapV2Factory(addr['ube_factory'])

    print("mobi:", core_oracle.getCELOPx(mobi))
    print("celo:", core_oracle.getCELOPx(celo))
    print("celo-mobi:", core_oracle.getCELOPx(ube_factory.getPair(mobi, celo)))
    
    # print("ube-celo", uni_oracle.getCELOPx(ube_factory.getPair(ube, celo)))
    # print("mcusd-btc", uni_oracle.getCELOPx(ube_factory.getPair(mcusd, btc)))
    # print("celo-mcusd", uni_oracle.getCELOPx(ube_factory.getPair(celo, mcusd)))
    # print("scelo-celo", uni_oracle.getCELOPx(ube_factory.getPair(scelo, celo)))
    # print("celo-mceur", uni_oracle.getCELOPx(ube_factory.getPair(celo, mceur)))