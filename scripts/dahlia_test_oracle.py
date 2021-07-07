from brownie import (SafeBox, HomoraBank, ERC20KP3ROracle, UniswapV2Oracle)
from brownie import accounts, interface, chain
from .utils import *
import json

def main():
    f = open('scripts/dahlia_addresses.json')
    addr = json.load(f)['mainnet']

    celo = interface.IERC20Ex(addr['celo'])
    ube = interface.IERC20Ex(addr['ube'])
    # btc = interface.IERC20Ex(addr['btc'])
    mcusd = interface.IERC20Ex(addr['mcusd'])
    mceur = interface.IERC20Ex(addr['mceur'])
    scelo = interface.IERC20Ex(addr['scelo'])
    kp3r_oracle = ERC20KP3ROracle.at(addr['kp3r_oracle'])
    uni_oracle = UniswapV2Oracle.at(addr['uni_oracle'])
    ube_factory = interface.IUniswapV2Factory(addr['ube_factory'])

    print("celo:", kp3r_oracle.getCELOPx(celo))
    print("ube:", kp3r_oracle.getCELOPx(ube))
    # print("btc:", kp3r_oracle.getCELOPx(btc))
    print("mcusd:", kp3r_oracle.getCELOPx(mcusd))
    print("mceur:", kp3r_oracle.getCELOPx(mceur))
    print("scelo:", kp3r_oracle.getCELOPx(scelo))

    print("ube-celo", uni_oracle.getCELOPx(ube_factory.getPair(ube, celo)))
    # print("mcusd-btc", uni_oracle.getCELOPx(ube_factory.getPair(mcusd, btc)))
    print("celo-mcusd", uni_oracle.getCELOPx(ube_factory.getPair(celo, mcusd)))
    print("scelo-celo", uni_oracle.getCELOPx(ube_factory.getPair(scelo, celo)))
    print("celo-mceur", uni_oracle.getCELOPx(ube_factory.getPair(celo, mceur)))