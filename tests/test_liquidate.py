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
            [10000, 10000, 10000],
            [10000, 10000, 10000],
            [10000, 10000, 10000],
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
        pos_id,
        spell,
        spell.addLiquidityWERC20.encode_input(
            token0,  # token 0
            token1,  # token 1
            [
                10 * 10**6,  # 10 cusd
                2 * 10**6,  # 2 ceur
                0,
                1000 * 10**6,  # 1000 cusd
                200 * 10**6,  # 200 ceur
                0,  # borrow LP tokens
                0,  # min cusd
                0,  # min ceur
            ],
        ),
        {'from': alice}
    )


def setup_bob(admin, bob, bank, ceur, cusd):
    ceur.mint(bob, 10000 * 10**6, {'from': admin})
    ceur.approve(bank, 2**256-1, {'from': bob})
    cusd.mint(bob, 10000 * 10**6, {'from': admin})
    cusd.approve(bank, 2**256-1, {'from': bob})


def test_liquidate(admin, alice, bob, bank, chain, werc20, ufactory, urouter, simple_oracle, oracle, celo, cusd, ceur, UniswapV2SpellV1, UniswapV2Oracle, core_oracle):
    setup_bob(admin, bob, bank, ceur, cusd)

    # execute
    spell = setup_uniswap(admin, alice, bank, werc20, urouter, ufactory, celo, cusd, ceur, chain,
                          UniswapV2Oracle, UniswapV2SpellV1, simple_oracle, core_oracle, oracle)
    execute_uniswap_werc20(admin, alice, bank, cusd, ceur, spell, ufactory, pos_id=0)

    pos_id = 1

    print('collateral value', bank.getCollateralETHValue(pos_id))
    print('borrow value', bank.getBorrowETHValue(pos_id))

    # bob tries to liquidate
    with brownie.reverts('position still healthy'):
        bank.liquidate(pos_id, ceur, 10 * 10**18, {'from': bob})

    # change oracle settings
    lp = ufactory.getPair(cusd, ceur)
    uniswap_lp_oracle = UniswapV2Oracle.deploy(simple_oracle, {'from': admin})
    oracle.setTokenFactors(
        [lp],
        [
            [10000, 9900, 10500],
        ],
        {'from': admin},
    )

    print('collateral value', bank.getCollateralETHValue(pos_id))
    print('borrow value', bank.getBorrowETHValue(pos_id))

    # ready to be liquidated
    bank.liquidate(pos_id, ceur, 100 * 10**6, {'from': bob})
    print('bob lp', werc20.balanceOfERC20(lp, bob))
    print('calc bob lp', 100 * 10**6 * simple_oracle.getCELOPx(ceur) //
          uniswap_lp_oracle.getCELOPx(lp) * 105 // 100)
    assert almostEqual(werc20.balanceOfERC20(lp, bob), 100 * 10**6 *
                       simple_oracle.getCELOPx(ceur) // uniswap_lp_oracle.getCELOPx(lp) * 105 // 100)

    print('collateral value', bank.getCollateralETHValue(pos_id))
    print('borrow value', bank.getBorrowETHValue(pos_id))

    oracle.setTokenFactors(
        [ceur, cusd],
        [
            [10700, 10000, 10300],
            [10200, 10000, 10100],
        ],
        {'from': admin},
    )

    print('collateral value', bank.getCollateralETHValue(pos_id))
    print('borrow value', bank.getBorrowETHValue(pos_id))

    # liquidate 300 cusd

    prevBobBal = werc20.balanceOfERC20(lp, bob)
    bank.liquidate(pos_id, cusd, 300 * 10**6, {'from': bob})
    curBobBal = werc20.balanceOfERC20(lp, bob)
    print('delta bob lp', curBobBal - prevBobBal)
    print('calc delta bob lp', 300 * 10**6 * simple_oracle.getCELOPx(cusd) //
          uniswap_lp_oracle.getCELOPx(lp) * 105 * 101 // 100 // 100)
    assert almostEqual(curBobBal - prevBobBal, 300 * 10**6 * simple_oracle.getCELOPx(cusd) //
                       uniswap_lp_oracle.getCELOPx(lp) * 105 * 101 // 100 // 100)

    # change cusd price
    simple_oracle.setCELOPx([cusd], [2**112 * 10**12 // 500])

    print('collateral value', bank.getCollateralETHValue(pos_id))
    print('borrow value', bank.getBorrowETHValue(pos_id))

    # liquidate max cusd (remaining 700)
    prevBobBal = werc20.balanceOfERC20(lp, bob)
    _, _, _, stCollSize = bank.getPositionInfo(pos_id)
    bank.liquidate(pos_id, cusd, 2**256-1, {'from': bob})
    curBobBal = werc20.balanceOfERC20(lp, bob)
    _, _, _, enCollSize = bank.getPositionInfo(pos_id)
    print('delta bob lp', curBobBal - prevBobBal)
    print('calc delta bob lp', stCollSize - enCollSize)
    assert almostEqual(curBobBal - prevBobBal, stCollSize - enCollSize)

    # try to liquidate more than available
    with brownie.reverts():
        bank.liquidate(pos_id, ceur, 101 * 10**6, {'from': bob})

    # liquidate 100 ceur (remaining 100)
    prevBobBal = werc20.balanceOfERC20(lp, bob)
    bank.liquidate(pos_id, ceur, 100 * 10**6, {'from': bob})
    curBobBal = werc20.balanceOfERC20(lp, bob)
    print('delta bob lp', curBobBal - prevBobBal)
    assert almostEqual(curBobBal - prevBobBal, 0)
