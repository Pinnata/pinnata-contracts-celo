import pytest
from brownie import interface

def almostEqual(a, b):
    thresh = 0.01
    return a <= b + thresh * abs(b) and a >= b - thresh * abs(b)


def test_uniswap_add_two_tokens(
    admin, alice, chain, bank, werc20, ufactory, urouter, simple_oracle, oracle, celo, cusd, ceur, UniswapV2SpellV1, UniswapV2Oracle, core_oracle
):
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
    uniswap_lp_oracle = UniswapV2Oracle.deploy(core_oracle, {'from': admin})

    print('ceur Px', simple_oracle.getCELOPx(ceur))
    print('cusd Px', simple_oracle.getCELOPx(cusd))

    core_oracle.setRoute([cusd, ceur, lp], [simple_oracle, simple_oracle, uniswap_lp_oracle])
    print('lp Px', uniswap_lp_oracle.getCELOPx(lp))

    oracle.setTokenFactors(
        [cusd, ceur, lp],
        [
            [11000, 9000, 10000],
            [11000, 9000, 10000],
            [11000, 9000, 10000],
        ],
        {'from': admin},
    )
    cusd.mint(alice, 10000000 * 10**6, {'from': admin})
    ceur.mint(alice, 10000000 * 10**6, {'from': admin})
    cusd.approve(bank, 2**256-1, {'from': alice})
    ceur.approve(bank, 2**256-1, {'from': alice})
    spell.getAndApprovePair(cusd, ceur, {'from': admin})
    lp = ufactory.getPair(cusd, ceur)
    spell.setWhitelistLPTokens([lp], [True], {'from': admin})
    bank.setWhitelistSpells([spell], [True], {'from': admin})
    bank.setWhitelistTokens([cusd, ceur], [True, True], {'from': admin})

    prevABal = cusd.balanceOf(alice)
    prevBBal = ceur.balanceOf(alice)

    initABal = prevABal
    initBBal = prevBBal

    for _ in range(40):
        tx = bank.execute(
            0,
            spell,
            spell.addLiquidityWERC20.encode_input(
                ceur,  # token 0
                cusd,  # token 1
                [
                    10000 * 10**6,  # 10000 ceur
                    10000 * 10**6,  # 10000 cusd
                    0,
                    4500 * 10**6,  # 1000 ceur
                    4500 * 10**6,  # 200 cusd
                    0,  # borrow LP tokens
                    0,  # min ceur
                    0,  # min cusd
                ],
            ),
            {'from': alice}
        )

    tx = bank.execute(
        0,
        spell,
        spell.addLiquidityWERC20.encode_input(
            ceur,  # token 0
            cusd,  # token 1
            [
                2000 * 10**5,  # 10000 ceur
                2000 * 10**5,  # 10000 cusd
                0,
                4000 * 10**5,  # 1000 ceur
                5000 * 10**5,  # 200 cusd
                0,  # borrow LP tokens
                0,  # min ceur
                0,  # min cusd
            ],
        ),
        {'from': alice}
    )

    curABal = ceur.balanceOf(alice)
    curBBal = cusd.balanceOf(alice)

    print('alice delta A Bal', curABal - prevABal)
    print('alice delta B Bal', curBBal - prevBBal)

    prevABal = cusd.balanceOf(alice)
    prevBBal = ceur.balanceOf(alice)

    position_id = bank.nextPositionId()

    prevBorrow = bank.getBorrowCELOValue(tx.return_value)
    chain.mine(50)
    chain.sleep(500)
    bank.accrue(cusd)
    bank.accrue(ceur)
    postBorrow = bank.getBorrowCELOValue(tx.return_value)
    assert (prevBorrow < postBorrow)

        # close the position
    bank.execute(
        position_id - 1,
        spell,
        spell.removeLiquidityWERC20.encode_input(
            cusd,
            ceur,
            [2**256-1, #lp to remove
             0, # lp to keep    
             2**256-1, #repay cusd
             2**256-1, #repay ceur
             0,
             0,
             0],
        ),
        {'from': alice}
    )

    curABal = cusd.balanceOf(alice)
    curBBal = ceur.balanceOf(alice)

    finalABal = curABal
    finalBBal = curBBal

    tokenAPrice = core_oracle.getCELOPx(cusd)
    tokenBPrice = core_oracle.getCELOPx(ceur)

    print('alice delta A Bal', curABal - prevABal)
    print('alice delta B Bal', curBBal - prevBBal)

    print('token A price', tokenAPrice)
    print('token B price', tokenBPrice)

    # assert almostEqual(tokenAPrice * initABal + tokenBPrice * initBBal,
    #                    tokenAPrice * finalABal + tokenBPrice * finalBBal), 'too much value lost'

    print('tx gas used', tx.gas_used)
    print('bank collateral size', bank.getPositionInfo(position_id))
    print('bank collateral value', bank.getCollateralCELOValue(position_id))
    print('bank borrow value', bank.getBorrowCELOValue(position_id))

    print('bank ceur', bank.getBankInfo(ceur))
    print('bank cusd', bank.getBankInfo(cusd))
    print('ceur Px', simple_oracle.getCELOPx(ceur))
    print('cusd Px', simple_oracle.getCELOPx(cusd))

    print('lp Px', uniswap_lp_oracle.getCELOPx(lp))
