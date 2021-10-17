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
    addr = json.load(f)['alfajores']
    position = 1016

    celo = interface.IERC20Ex(addr['celo'])
    cusd = interface.IERC20Ex(addr['cusd'])
    ceur = interface.IERC20Ex(addr['ceur'])
    fcelo = interface.ICErc20(addr['fcelo'])
    fcusd = interface.ICErc20(addr['fcusd'])
    fceur = interface.ICErc20(addr['fceur'])
    dahlia_bank = Contract.from_abi("HomoraBank", addr.get('dahlia_bank'), HomoraBank.abi)
    # dahlia_bank.setFeeBps(10, {'from': deployer})

    dahlia_bank.accrue(celo, {'from': person})
    dahlia_bank.accrue(cusd, {'from': person})
    dahlia_bank.accrue(ceur, {'from': person})

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
    assert dahlia_bank.getBankInfo(cusd)[3] == fcusd.borrowBalanceStored(dahlia_bank.address)
    assert dahlia_bank.getBankInfo(ceur)[3] == fceur.borrowBalanceStored(dahlia_bank.address)
