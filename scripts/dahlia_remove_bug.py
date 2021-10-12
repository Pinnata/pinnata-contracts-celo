from os import error
from brownie import (
    accounts,
    interface,
    Contract,
    HomoraBank,
    network
)
import json

network.gas_limit(8000000)

def main():
    deployer = accounts.load('dahlia_admin')
    person = accounts.load('dahlia_alice')
    f = open('scripts/dahlia_addresses.json')
    addr = json.load(f)['mainnet']
    position = 3

    celo = interface.IERC20Ex(addr['celo'])
    mcusd = interface.IERC20Ex(addr['mcusd'])
    mceur = interface.IERC20Ex(addr['mceur'])
    scelo = interface.IERC20Ex(addr['scelo'])
    ube = interface.IERC20Ex(addr['ube'])
    fcelo = interface.ICErc20(addr['fcelo'])
    fmcusd = interface.ICErc20(addr['fmcusd'])
    fmceur = interface.ICErc20(addr['fmceur'])
    fscelo = interface.ICErc20(addr['fscelo'])
    fube = interface.ICErc20(addr['fube'])
    dahlia_bank = Contract.from_abi("HomoraBank", addr.get('dahlia_bank'), HomoraBank.abi)
    # dahlia_bank.setFeeBps(10, {'from': deployer})

    # dahlia_bank.accrue(celo, {'from': person})
    # dahlia_bank.accrue(mcusd, {'from': person})
    # dahlia_bank.accrue(mceur, {'from': person})
    # dahlia_bank.accrue(scelo, {'from': person})
    # dahlia_bank.accrue(ube, {'from': person})

    (owner, collToken, collId, collateralsize) = dahlia_bank.getPositionInfo(position)
    collat = dahlia_bank.getCollateralCELOValue(position)
    borrow = dahlia_bank.getBorrowCELOValue(position)
    print("collateral value:", collat)
    print("borrow value:", borrow)
    print("owner:", owner)
    print("collToken:", collToken)
    print("collId:", collId)
    print("collateral size:", collateralsize)

    assert dahlia_bank.getBankInfo(celo)[3] == fcelo.borrowBalanceStored(dahlia_bank.address)
    assert dahlia_bank.getBankInfo(mcusd)[3] == fmcusd.borrowBalanceStored(dahlia_bank.address)
    assert dahlia_bank.getBankInfo(mceur)[3] == fmceur.borrowBalanceStored(dahlia_bank.address)
    assert dahlia_bank.getBankInfo(scelo)[3] == fscelo.borrowBalanceStored(dahlia_bank.address)
    assert dahlia_bank.getBankInfo(ube)[3] == fube.borrowBalanceStored(dahlia_bank.address)