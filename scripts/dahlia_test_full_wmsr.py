from brownie import (
    accounts,
    WMStakingRewards, 
    ProxyOracle,
    interface,
    network,
    WERC20,
    Contract,
    UbeswapMSRSpellV1,
    HomoraBank,
    SafeBox
)

import json
import time

network.gas_limit(8000000)

def lend(bob, token, safebox):
    token.approve(safebox, 2**256-1, {'from': bob})

    bob_amt = 10**16
    safebox.deposit(bob_amt, {'from': bob})

def main():
    deployer = accounts.load('dahlia_admin')
    alice = accounts.load('dahlia_alice')
    bob = accounts.load('dahlia_bob')

    with open('scripts/dahlia_addresses.json', 'r') as f:
        addr = json.load(f)
    sub_addr = addr.get('alpha')

    ube = interface.IERC20Ex(sub_addr.get('ube'))
    mobi = interface.IERC20Ex(sub_addr.get('mobi'))
    celo = interface.IERC20Ex(sub_addr.get('celo'))
    ube_factory = interface.IUniswapV2Factory(sub_addr.get('ube_factory'))
    ube_router = interface.IUniswapV2Router02(sub_addr.get('ube_router'))
    proxy_oracle = ProxyOracle.at(sub_addr.get('proxy_oracle'))
    celo_mobi_mstaking = sub_addr.get('celo_mobi_mstaking')
    celo_ube_mstaking = sub_addr.get('celo_ube_mstaking')

    werc20 = WERC20.at(sub_addr.get('werc20'))
    dahlia_bank = Contract.from_abi("HomoraBank", sub_addr.get('dahlia_bank'), HomoraBank.abi)

    celo_mobi_lp = ube_factory.getPair(celo, mobi)
    celo_ube_lp = ube_factory.getPair(celo, ube)

    celo_safebox = SafeBox.at(sub_addr.get('dcelo'))
    mobi_safebox = SafeBox.at(sub_addr.get('dmobi'))

    celo_mobi_wmstaking = WMStakingRewards.deploy(
        celo_mobi_mstaking,
        celo_mobi_lp,
        [celo, ube, mobi],
        3,
        {'from': deployer}
    )

    celo_ube_wmstaking = WMStakingRewards.deploy(
        celo_ube_mstaking,
        celo_ube_lp,
        [celo, ube],
        2,
        {'from': deployer}
    )

    proxy_oracle.setWhitelistERC1155(
        [celo_mobi_wmstaking, celo_ube_wmstaking],
        True,
        {'from': deployer},
    )

    ubeswap_spell = UbeswapMSRSpellV1.deploy(
        dahlia_bank, werc20, ube_router, celo,
        {'from': deployer},
    )

    ubeswap_spell.getAndApprovePair(celo, mobi, {'from': deployer})
    ubeswap_spell.getAndApprovePair(celo, ube, {'from': deployer})

    ubeswap_spell.setWhitelistLPTokens([celo_mobi_lp, celo_ube_lp], [True, True], {'from': deployer})

    dahlia_bank.setWhitelistSpells([ubeswap_spell], [True], {'from': deployer})

    celo.approve(dahlia_bank, 2**256-1, {'from': alice})
    mobi.approve(dahlia_bank, 2**256-1, {'from': alice})

    lend(bob, celo, celo_safebox)
    lend(bob, mobi, mobi_safebox)

    # open a position
    dahlia_bank.execute(
        0,
        ubeswap_spell,
        ubeswap_spell.addLiquidityWStakingRewards.encode_input(
            mobi,
            celo,
            [
             6*10**14,
             10**14,
             0,
             0,
             0,
             0,
             0,
             0
            ],
            celo_mobi_wmstaking
        ),
        {
            'from': alice, 
        }
    )
    
    addr.get('alpha').update({
        'celo_mobi_wmstaking': celo_mobi_wmstaking.address,
        'celo_ube_wmstaking': celo_ube_wmstaking.address,
        'ubeswap_spell': ubeswap_spell.address,
    })

    print(json.dumps(addr, indent=4), file=open('scripts/dahlia_addresses.json', 'w'))
