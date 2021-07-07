from brownie import (
    accounts, ProxyOracle, CoreOracle,
    HomoraBank, CurveOracle
)
from brownie import interface
from .utils import *

def main():
    deployer = accounts.load('admin')

    core_oracle = CoreOracle.deploy({'from': deployer})
    proxy_oracle = ProxyOracle.deploy(core_oracle, {'from': deployer})

    # TODO: use proxy openzeppelin contract
    # bank_impl = HomoraBank.deploy({'from': deployer})
    # bank_impl.initialize(proxy_oracle, 0, {'from': deployer})
    # bank = TransparentUpgradableProxy(bank_impl, deployer, {'from': deployer})
    
    bank = HomoraBank.deploy({'from': deployer})
    bank.initialize(proxy_oracle, 0, {'from': deployer})

    print('Done!')