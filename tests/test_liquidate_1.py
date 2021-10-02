import pytest
from brownie import interface
import brownie
from utils import *


def setup_uniswap(admin, alice, bank, werc20, urouter, ufactory, celo, cusd, ceur, chain, UniswapV2Oracle, UniswapV2SpellV1, simple_oracle, core_oracle, oracle):
    spell = UniswapV2SpellV1.deploy(bank, werc20, urouter, celo, {'from': admin})
    cusd.mint(admin, 10000000 * 10**6, {'from': admin})
    ceur.mint(admin, 10000000 * 10**6, {'from': admin})
    cusd.approve(urouter, 2**256-1, {'from': admin})
    ceur.approve(urouter, 2**256-1, {'from': admin})
    urouter.addLiquidity(
        cusd,
        ceur,
        1000000 * 10**6,
        1000000 * 10**6,
        0,
        0,
        admin,
        chain.time() + 60,
        {'from': admin},
    )

    lp = ufactory.getPair(cusd, ceur)
    print('admin lp bal', interface.IERC20(lp).balanceOf(admin))
    uniswap_lp_oracle = UniswapV2Oracle.deploy(simple_oracle, {'from': admin})

    print('ceur Px', simple_oracle.getCELOPx(ceur))
    print('cusd Px', simple_oracle.getCELOPx(cusd))

    core_oracle.setRoute([cusd, ceur, lp], [simple_oracle, simple_oracle, uniswap_lp_oracle])
    print('lp Px', uniswap_lp_oracle.getCELOPx(lp))
    oracle.setTokenFactors(
        [cusd, ceur, lp],
        [
            [11000, 9000, 10500],
            [11000, 9000, 10500],
            [11000, 9000, 10500],
        ],
        {'from': admin},
    )
    cusd.mint(alice, 10000000 * 10**6, {'from': admin})
    ceur.mint(alice, 10000000 * 10**6, {'from': admin})
    cusd.approve(bank, 2**256-1, {'from': alice})
    ceur.approve(bank, 2**256-1, {'from': alice})

    return spell


def execute_uniswap_werc20(admin, alice, bank, token0, token1, spell, ufactory, pos_id=0):
    spell.getAndApprovePair(token0, token1, {'from': admin})
    lp = ufactory.getPair(token0, token1)
    spell.setWhitelistLPTokens([lp], [True], {'from': admin})
    bank.setWhitelistSpells([spell], [True], {'from': admin})
    bank.setWhitelistTokens([token0, token1], [True, True], {'from': admin})
    tx = bank.execute(
        0,
        spell,
        spell.addLiquidityWERC20.encode_input(
            token0,  # token 0
            token1,  # token 1
            [
                10000 * 10**6,  # 10000 ceur
                10000 * 10**6,  # 10000 cusd
                0,
                44999 * 10**6,  # levered to the tits
                44999 * 10**6,  #
                0,  # borrow LP tokens
                0,  # min ceur
                0,  # min cusd
            ],
        ),
        {'from': alice}
    )


def setup_bob(admin, bob, bank, ceur, cusd):
    ceur.mint(bob, 100000 * 10**6, {'from': admin})
    ceur.approve(bank, 2**256-1, {'from': bob})
    cusd.mint(bob, 100000 * 10**6, {'from': admin})
    cusd.approve(bank, 2**256-1, {'from': bob})


def test_liquidate(admin, alice, bob, bank, chain, werc20, ufactory, urouter, simple_oracle, oracle, celo, cusd, ceur, UniswapV2SpellV1, UniswapV2Oracle, core_oracle):
    setup_bob(admin, bob, bank, ceur, cusd)

    # execute
    spell = setup_uniswap(admin, alice, bank, werc20, urouter, ufactory, celo, cusd, ceur, chain,
                          UniswapV2Oracle, UniswapV2SpellV1, simple_oracle, core_oracle, oracle)
    execute_uniswap_werc20(admin, alice, bank, cusd, ceur, spell, ufactory, pos_id=0)

    pos_id = 1

    print('collateral value', bank.getCollateralCELOValue(pos_id))
    print('borrow value', bank.getBorrowCELOValue(pos_id))

    # bob tries to liquidate
    with brownie.reverts('position still healthy'):
        bank.liquidate(pos_id, ceur, 10 * 10**18, {'from': bob})

    # # change oracle settings
    lp = ufactory.getPair(cusd, ceur)
    uniswap_lp_oracle = UniswapV2Oracle.deploy(simple_oracle, {'from': admin})
    
    chain.mine(50)
    chain.sleep(50000)
    bank.accrue(cusd)
    bank.accrue(ceur)

    print('collateral value', bank.getCollateralCELOValue(pos_id))
    print('borrow value', bank.getBorrowCELOValue(pos_id))

    # ready to be liquidated
    bank.liquidate(pos_id, ceur, 100 * 10**6, {'from': bob})
    print('bob lp', werc20.balanceOfERC20(lp, bob))
    print('calc bob lp', 100 * 10**6 * simple_oracle.getCELOPx(ceur) //
          uniswap_lp_oracle.getCELOPx(lp) * 105 // 100)
    assert almostEqual(werc20.balanceOfERC20(lp, bob), 100 * 10**6 *
                       simple_oracle.getCELOPx(ceur) // uniswap_lp_oracle.getCELOPx(lp) * 105 * 105 // 100 // 100)

    print('collateral value', bank.getCollateralCELOValue(pos_id))
    print('borrow value', bank.getBorrowCELOValue(pos_id))
