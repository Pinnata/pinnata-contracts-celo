import pytest
from brownie import interface
import brownie


def setup_uniswap(admin, alice, bank, werc20, urouter, ufactory, cusd, ceur, chain, UniswapV2Oracle, UniswapV2SpellV1, simple_oracle, core_oracle, oracle):
    spell = UniswapV2SpellV1.deploy(bank, werc20, urouter, {'from': admin})
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
        2**256-1,
        {'from': admin},
    )

    lp = ufactory.getPair(cusd, ceur)
    print('admin lp bal', interface.IERC20(lp).balanceOf(admin))
    uniswap_lp_oracle = UniswapV2Oracle.deploy(core_oracle, {'from': admin})

    print('ceur Px', simple_oracle.getCELOPx(ceur))
    print('cusd Px', simple_oracle.getCELOPx(cusd))

    core_oracle.setRoute([cusd, ceur, lp], [simple_oracle, simple_oracle,
                                            uniswap_lp_oracle], {'from': admin})

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
