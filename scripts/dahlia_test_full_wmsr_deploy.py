from brownie import (
    accounts,
    interface,
    network,
    MockERC20,
    MockStakingRewards,
    MockMoolaStakingRewards,
    WMStakingRewards,
    ProxyOracle,
    Contract,
    UbeswapMSRSpellV1,
    WERC20,
    HomoraBank,
)
import json

network.gas_limit(8000000)

zero_add = '0x0000000000000000000000000000000000000000'

def main():
    deployer = accounts.load('dahlia_admin')
    alice = accounts.load('dahlia_alice')

    with open('scripts/dahlia_addresses.json', 'r') as f:
        addr = json.load(f)

    alfajores_addr = addr.get('alfajores')

    celo = interface.IERC20Ex(alfajores_addr.get('celo'))
    cusd = interface.IERC20Ex(alfajores_addr.get('cusd'))
    ceur = interface.IERC20Ex(alfajores_addr.get('ceur'))
    mock = interface.IERC20Ex(alfajores_addr.get('mock'))
    celo_cusd_staking = MockStakingRewards.at(alfajores_addr.get('celo_cusd_staking'))
    celo_ceur_staking = MockStakingRewards.at(alfajores_addr.get('celo_ceur_staking'))
    cusd_ceur_staking = MockStakingRewards.at(alfajores_addr.get('cusd_ceur_staking'))
    urouter = interface.IUniswapV2Router02(alfajores_addr.get('urouter'))
    ufactory = interface.IUniswapV2Factory(alfajores_addr.get('ufactory'))
    proxy_oracle = ProxyOracle.at(alfajores_addr.get('proxy_oracle'))

    celo_cusd_lp = ufactory.getPair(celo, cusd)
    celo_ceur_lp = ufactory.getPair(celo, ceur)
    cusd_ceur_lp = ufactory.getPair(cusd, ceur)

    mock2 = MockERC20.deploy('Mother', 'MOM', 18, {'from': deployer})

    # mock.mint(celo_cusd_staking, 1000*10**18, {'from': deployer})
    # mock.mint(celo_ceur_staking, 1000*10**18, {'from': deployer})
    # mock.mint(cusd_ceur_staking, 1000*10**18, {'from': deployer})

    # celo_cusd_staking.setRewardsDuration(60*60*24*7, {'from': deployer})
    # celo_ceur_staking.setRewardsDuration(60*60*24*7, {'from': deployer})
    # cusd_ceur_staking.setRewardsDuration(60*60*24*7, {'from': deployer})

    # celo_cusd_staking.notifyRewardAmount(500*10**18, {'from': deployer})
    # celo_ceur_staking.notifyRewardAmount(500*10**18, {'from': deployer})
    # cusd_ceur_staking.notifyRewardAmount(500*10**18, {'from': deployer})

    celo_cusd_multi_staking = MockMoolaStakingRewards.deploy(deployer, deployer, mock2, celo_cusd_staking, [mock], celo_cusd_lp, {'from': deployer})
    # celo_ceur_multi_staking = MockMoolaStakingRewards.deploy(deployer, deployer, mock2, celo_ceur_staking, [mock], celo_ceur_lp, {'from': deployer})
    # cusd_ceur_multi_staking = MockMoolaStakingRewards.deploy(deployer, deployer, mock2, cusd_ceur_staking, [mock], cusd_ceur_lp, {'from': deployer})

    mock2.mint(celo_cusd_multi_staking, 1000*10**18, {'from': deployer})
    # mock2.mint(celo_ceur_multi_staking, 1000*10**18, {'from': deployer})
    # mock2.mint(cusd_ceur_multi_staking, 1000*10**18, {'from': deployer})

    celo_cusd_multi_staking.setRewardsDuration(60*60*24*7, {'from': deployer})
    # celo_ceur_multi_staking.setRewardsDuration(60*60*24*7, {'from': deployer})
    # cusd_ceur_multi_staking.setRewardsDuration(60*60*24*7, {'from': deployer})

    celo_cusd_multi_staking.notifyRewardAmount(100*10**18, {'from': deployer})
    # celo_ceur_multi_staking.notifyRewardAmount(100*10**18, {'from': deployer})
    # cusd_ceur_multi_staking.notifyRewardAmount(100*10**18, {'from': deployer})

    celo_cusd_wmstaking = WMStakingRewards.deploy(
        celo_cusd_multi_staking,
        celo_cusd_lp,
        [mock2, mock, zero_add, zero_add, zero_add, zero_add, zero_add, zero_add],
        2,
        {'from': deployer}
    )

    # celo_ceur_wmstaking = WMStakingRewards.deploy(
    #     celo_ceur_multi_staking,
    #     celo_ceur_lp,
    #     mock2,
    #     2,
    #     {'from': deployer}
    # )

    # cusd_ceur_wmstaking = WMStakingRewards.deploy(
    #     cusd_ceur_multi_staking,
    #     cusd_ceur_lp,
    #     mock2,
    #     2,
    #     {'from': deployer}
    # )

    proxy_oracle.setWhitelistERC1155(
        [celo_cusd_wmstaking], #, celo_ceur_wmstaking, cusd_ceur_wmstaking],
        True,
        {'from': deployer},
    )

    werc20 = WERC20.at(alfajores_addr.get('werc20'))
    dahlia_bank = Contract.from_abi("HomoraBank", alfajores_addr.get('dahlia_bank'), HomoraBank.abi)

    ubeswap_spell = UbeswapMSRSpellV1.deploy(
        dahlia_bank, werc20, urouter, celo,
        {'from': deployer},
    )

    ubeswap_spell.getAndApprovePair(celo, cusd, {'from': deployer})
    # ubeswap_spell.getAndApprovePair(celo, ceur, {'from': deployer})
    # ubeswap_spell.getAndApprovePair(cusd, ceur, {'from': deployer})

    ubeswap_spell.setWhitelistLPTokens([celo_cusd_lp, celo_ceur_lp, cusd_ceur_lp], [True, True, True], {'from': deployer})

    dahlia_bank.setWhitelistSpells([ubeswap_spell], [True], {'from': deployer})

    celo.approve(dahlia_bank, 2**256-1, {'from': alice})
    cusd.approve(dahlia_bank, 2**256-1, {'from': alice})

    prevABal = celo.balanceOf(alice)
    prevBBal = cusd.balanceOf(alice)

    initABal = prevABal
    initBBal = prevBBal

    print('prev A bal', prevABal)
    print('prev B bal', prevBBal)

    prevRewards = mock.balanceOf(alice)

    # open a position
    dahlia_bank.execute(
        0,
        ubeswap_spell,
        ubeswap_spell.addLiquidityWStakingRewards.encode_input(
            cusd,
            celo,
            [
             6*10**16,
             10**16,
             0,
             9*10**16,
             1.5*10**16,
             0,
             0,
             0
            ],
            celo_cusd_wmstaking
        ),
        {
            'from': alice, 
        }
    )

    # addr.get('alfajores').update({
    #     'mock2': mock2.address,
    #     'celo_cusd_mstaking': celo_cusd_multi_staking.address,
    #     'celo_ceur_mstaking': celo_ceur_multi_staking.address,
    #     'cusd_ceur_mstaking': cusd_ceur_multi_staking.address,
    #     'celo_cusd_wmstaking': celo_cusd_wmstaking.address,
    #     'celo_ceur_wmstaking': celo_ceur_wmstaking.address,
    #     'cusd_ceur_wmstaking': cusd_ceur_wmstaking.address,
    # })

    print(json.dumps(addr, indent=4), file=open('scripts/dahlia_addresses.json', 'w'))