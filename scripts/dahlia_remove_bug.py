from os import error
from brownie import accounts, interface, Contract
from brownie import (
    HomoraBank,
    MockERC20, CoreOracle, UniswapV2Oracle, SimpleOracle, UniswapV2SpellV1, WERC20, SafeBox, WStakingRewards, network
)
import json
import time

network.gas_limit(8000000)


def almostEqual(a, b):
    thresh = 0.01
    return a <= b + thresh * abs(b) and a >= b - thresh * abs(b)


def lend(bob, token, safebox):
    token.approve(safebox, 2**256-1, {'from': bob})

    bob_amt = 10**15
    safebox.deposit(bob_amt, {'from': bob})


def main():
    deployer = accounts.load('dahlia_admin')
    alice = accounts.load('dahlia_alice')
    kyle = accounts.load('kyle_personal')
    f = open('scripts/dahlia_addresses.json')
    addr = json.load(f)['alfajores']

    celo = interface.IERC20Ex(addr['celo'])
    cusd = interface.IERC20Ex(addr['cusd'])
    ceur = interface.IERC20Ex(addr['ceur'])
    dahlia_bank = Contract.from_abi("HomoraBank", addr.get('dahlia_bank'), HomoraBank.abi)
    uniswap_spell = UniswapV2SpellV1.at(addr['uni_spell'])
    wstaking = WStakingRewards.at(addr['cusd_ceur_wstaking'])
    mock = MockERC20.at(addr['mock'])

    prevRewards = mock.balanceOf(alice)

    print("wstaking:", wstaking)
    dahlia_bank.accrue(cusd, {'from': deployer})
    dahlia_bank.accrue(ceur, {'from': deployer})

        # (owner, collToken, collId, collateralsize) = dahlia_bank.getPositionInfo(i)
        # collat = dahlia_bank.getCollateralCELOValue(i)
        # borrow = dahlia_bank.getBorrowCELOValue(i)
        # print(dahlia_bank.getPositionDebts(i))
        # print("collateral value:", collat)
        # print("borrow value:", borrow)
        # print("owner:", owner)
        # print("collToken:", collToken)
        # print("collId:", collId)
        # print("collateral size:", collateralsize)
        # debts = {
        # "dcelo": "0x325416cb0d7c18457B4538F53525C51F92762FA2",
        # "dcusd": "0x95f06d7CE0014a655ede3690314e6440816Db0BD",
        # "dceur": "0x701FcC5914b0cEb34CdEd76474b731ec6d4a9D21",
        # }
        # dahlia_bank.setFeeBps(10, {'from': deployer})
        # dahlia_bank.accrue(celo, {'from': deployer})
        # print('bank info', dahlia_bank.getBankInfo(celo))
        # print('ftoken balance of dahlia', fcelo.borrowBalanceStored(dahlia_bank.address))
        # dahlia_bank.accrue(celo, {'from': deployer})
        # print('called accrue, which updates the ctoken and dahlia bank interest')
        # print('bank info', dahlia_bank.getBankInfo(celo))
        # fcusd.borrowBalanceCurrent(dahlia_bank.address, {'from': deployer})
        # dahlia_bank.accrue(celo, {'from': deployer})
        # dahlia_bank.accrue(cusd, {'from': deployer})
        # print('==============')
        # print('ctoken values')
        # print(fcelo.borrowBalanceStored(dahlia_bank.address))
        # print(fcusd.borrowBalanceStored(dahlia_bank.address))
        # print(dahlia_bank.feeBps())
        # print('bank info')
        # print(dahlia_bank.getBankInfo(celo))
        # print(dahlia_bank.getBankInfo(cusd))
        # print('borrow balance')
        # print(dahlia_bank.borrowBalanceStored(27, celo, {'from': alice}))
        # print(dahlia_bank.borrowBalanceStored(27, cusd, {'from': alice}))
        # print('position debt share')
        # print(dahlia_bank.getPositionDebtShareOf(27, celo))
        # print(dahlia_bank.getPositionDebtShareOf(27, cusd))
        # time.sleep(300)
        # fcelo.borrowBalanceCurrent(dahlia_bank.address, {'from': deployer})
        # fcusd.borrowBalanceCurrent(dahlia_bank.address, {'from': deployer})
        # dahlia_bank.accrue(celo, {'from': deployer})
        # dahlia_bank.accrue(cusd, {'from': deployer})
        # print('ctoken values')
        # print(fcelo.borrowBalanceStored(dahlia_bank.address))
        # print(fcusd.borrowBalanceStored(dahlia_bank.address))
        # print('bank info')
        # print(dahlia_bank.getBankInfo(celo))
        # print(dahlia_bank.getBankInfo(cusd))
        # print('borrow balance')
        # print(dahlia_bank.borrowBalanceStored(27, celo, {'from': alice}))
        # print(dahlia_bank.borrowBalanceStored(27, cusd, {'from': alice}))
        # print('position debt share')
        # print(dahlia_bank.getPositionDebtShareOf(27, celo))
        # print(dahlia_bank.getPositionDebtShareOf(27, cusd))
        # print(dahlia_bank.getBankInfo(celo))
        # print(dahlia_bank.getBankInfo(cusd))

    dahlia_bank.execute(
        12,
        uniswap_spell,
        uniswap_spell.removeLiquidityWStakingRewards.encode_input(
            cusd,
            ceur,
            [2**256-1,
            0,
            2**256-1,
            2**256-1,
            0,
            0,
            0],
            wstaking
        ),
        {'from': kyle}
    )

    postRewards = mock.balanceOf(alice)

    print(prevRewards)
    print(postRewards)
