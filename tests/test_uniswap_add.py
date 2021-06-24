import pytest
from brownie import interface


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
    spell.getAndApprovePair(cusd, ceur, {'from': admin})
    lp = ufactory.getPair(cusd, ceur)
    spell.setWhitelistLPTokens([lp], [True], {'from': admin})
    bank.setWhitelistSpells([spell], [True], {'from': admin})
    bank.setWhitelistTokens([cusd, ceur], [True, True], {'from': admin})
    tx = bank.execute(
        0,
        spell,
        spell.addLiquidityWERC20.encode_input(
            ceur,  # token 0
            cusd,  # token 1
            [
                40000 * 10**6,  # 40000 ceur
                50000 * 10**6,  # 50000 cusd
                0,
                1000 * 10**6,  # 1000 ceur
                200 * 10**6,  # 200 cusd
                0,  # borrow LP tokens
                0,  # min ceur
                0,  # min cusd
            ],
        ),
        {'from': alice}
    )

    position_id = tx.return_value
    print('tx gas used', tx.gas_used)
    print('bank collateral size', bank.getPositionInfo(position_id))
    print('bank collateral value', bank.getCollateralETHValue(position_id))
    print('bank borrow value', bank.getBorrowETHValue(position_id))

    print('bank ceur', bank.getBankInfo(ceur))
    print('bank cusd', bank.getBankInfo(cusd))

    print('ceur Px', simple_oracle.getCELOPx(ceur))
    print('cusd Px', simple_oracle.getCELOPx(cusd))

    print('lp Px', uniswap_lp_oracle.getCELOPx(lp))
