from brownie import (
    accounts, ERC20KP3ROracle, UniswapV2Oracle, BalancerPairOracle, ProxyOracle, CoreOracle,
    HomoraBank, CurveOracle, UniswapV2SpellV1, WERC20, WLiquidityGauge, WMasterChef,
    WStakingRewards, SushiswapSpellV1, BalancerSpellV1, CurveSpellV1, UbeswapV1Oracle, SafeBox
)
from brownie import interface
from .utils import *


def almostEqual(a, b):
    thresh = 0.01
    return a <= b + thresh * abs(b) and a >= b - thresh * abs(b)


def test_uniswap_spell(uniswap_spell, homora, oracle):
    alice = accounts[0]

    celo_addr = '0xf194afdf50b03e69bd7d057c1aa9e10c9954e4c9'
    cusd_addr = '0x874069fa1eb16d44d622f2e0ca25eea172369bc1'

    celo = interface.IERC20Ex(celo_addr)
    cusd = interface.IERC20Ex(cusd_addr)

    mint_tokens(celo, alice)
    mint_tokens(celo, alice)

    cusd.approve(homora, 2**256-1, {'from': alice})
    celo.approve(homora, 2**256-1, {'from': alice})

    prevABal = cusd.balanceOf(alice)
    prevBBal = celo.balanceOf(alice)
    prevETHBal = alice.balance()

    initABal = prevABal
    initBBal = prevBBal
    initETHBal = prevETHBal

    print('prev A bal', prevABal)
    print('prev B bal', prevBBal)

    # open a position
    homora.execute(
        0,
        uniswap_spell,
        uniswap_spell.addLiquidityWERC20.encode_input(
            cusd,
            celo,
            [10**18,
             10**18,
             0,
             10**18,
             10**18,
             0,
             0,
             0],
        ),
        {'from': alice}
    )

    curABal = cusd.balanceOf(alice)
    curBBal = celo.balanceOf(alice)

    print('alice delta A Bal', curABal - prevABal)
    print('alice delta B Bal', curBBal - prevBBal)

    prevABal = cusd.balanceOf(alice)
    prevBBal = celo.balanceOf(alice)
    prevETHBal = alice.balance()

    position_id = homora.nextPositionId()

    # close the position
    homora.execute(
        position_id - 1,
        uniswap_spell,
        uniswap_spell.removeLiquidityWERC20.encode_input(
            cusd,
            celo,
            [2**256-1,
             0,
             2**256-1,
             2**256-1,
             0,
             0,
             0],
        ),
        {'from': alice}
    )

    curABal = cusd.balanceOf(alice)
    curBBal = celo.balanceOf(alice)
    curETHBal = alice.balance()

    finalABal = curABal
    finalBBal = curBBal
    finalETHBal = curETHBal

    tokenAPrice = oracle.getCELOPx(cusd)
    tokenBPrice = oracle.getCELOPx(celo)
    tokenETHPrice = oracle.getCELOPx('0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE')

    print('alice delta A Bal', curABal - prevABal)
    print('alice delta B Bal', curBBal - prevBBal)
    print('alice delta ETH Bal', curETHBal - prevETHBal)

    print('token A price', tokenAPrice)
    print('token B price', tokenBPrice)
    print('token ETH price', tokenETHPrice)

    assert almostEqual(tokenAPrice * initABal + tokenBPrice * initBBal + tokenETHPrice * initETHBal,
                       tokenAPrice * finalABal + tokenBPrice * finalBBal + tokenETHPrice * finalETHBal), 'too much value lost'


def test_uniswap_spell_wstaking(uniswap_spell, homora, wstaking, oracle):
    alice = accounts[0]

    dpi = interface.IERC20Ex('0x1494ca1f11d487c2bbe4543e90080aeba4ba3c2b')
    celo = interface.IERC20Ex('0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2')
    index = interface.IERC20Ex('0x0954906da0bf32d5479e25f46056d22f08464cab')

    mint_tokens(dpi, alice)
    mint_tokens(celo, alice)

    dpi.approve(homora, 2**256-1, {'from': alice})
    celo.approve(homora, 2**256-1, {'from': alice})

    prevABal = dpi.balanceOf(alice)
    prevBBal = celo.balanceOf(alice)
    prevETHBal = alice.balance()

    initABal = prevABal
    initBBal = prevBBal
    initETHBal = prevETHBal

    print('prev A bal', prevABal)
    print('prev B bal', prevBBal)

    # open a position
    homora.execute(
        0,
        uniswap_spell,
        uniswap_spell.addLiquidityWStakingRewards.encode_input(
            dpi,
            celo,
            [10**18,
             10**18,
             0,
             0,
             5 * 10**17,
             0,
             0,
             0],
            wstaking
        ),
        {'from': alice}
    )

    curABal = dpi.balanceOf(alice)
    curBBal = celo.balanceOf(alice)

    print('alice delta A Bal', curABal - prevABal)
    print('alice delta B Bal', curBBal - prevBBal)

    prevABal = dpi.balanceOf(alice)
    prevBBal = celo.balanceOf(alice)
    prevETHBal = alice.balance()

    position_id = homora.nextPositionId()

    # close the position
    homora.execute(
        position_id - 1,
        uniswap_spell,
        uniswap_spell.removeLiquidityWStakingRewards.encode_input(
            dpi,
            celo,
            [2**256-1,
             0,
             0,
             2**256-1,
             0,
             0,
             0],
            wstaking
        ),
        {'from': alice}
    )

    curABal = dpi.balanceOf(alice)
    curBBal = celo.balanceOf(alice)
    curETHBal = alice.balance()

    finalABal = curABal
    finalBBal = curBBal
    finalETHBal = curETHBal

    tokenAPrice = oracle.getCELOPx(dpi)
    tokenBPrice = oracle.getCELOPx(celo)
    tokenETHPrice = oracle.getCELOPx('0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE')

    print('alice delta A Bal', curABal - prevABal)
    print('alice delta B Bal', curBBal - prevBBal)
    print('alice delta ETH Bal', curETHBal - prevETHBal)

    print('token A price', tokenAPrice)
    print('token B price', tokenBPrice)
    print('token ETH price', tokenETHPrice)

    print('index reward', index.balanceOf(alice))

    assert almostEqual(tokenAPrice * initABal + tokenBPrice * initBBal + tokenETHPrice * initETHBal,
                       tokenAPrice * finalABal + tokenBPrice * finalBBal + tokenETHPrice * finalETHBal), 'too much value lost'

    assert index.balanceOf(alice) > 0, 'should get some INDEX reward'
 

def main():
    # deployer = accounts.at('0xB593d82d53e2c187dc49673709a6E9f806cdC835', force=True)
    deployer = accounts.load('gh')
    werc20 = WERC20.deploy({'from': deployer})

    celo_addr = '0xf194afdf50b03e69bd7d057c1aa9e10c9954e4c9'
    cusd_addr = '0x874069fa1eb16d44d622f2e0ca25eea172369bc1'
    ceur_addr = '0x10c892A6EC43a53E45D0B916B4b7D383B1b78C0F'
    ube_addr = '0xbe413cdfdad27e71cf533882c760a91ecd02ab27'
    ube_celo_pool_addr = '0xAd2E17dad4aE46C8e797316ad44BEEF21D105624'
    ube_router_addr = '0xE3D8bd6Aed4F159bc8000a9cD47CffDb95F96121'

    # TODO: add ubeswap farming position 
    # wsube = WStakingRewards.deploy(
    #     '0xB93b505Ed567982E2b6756177ddD23ab5745f309',
    #     '0x4d5ef58aAc27d99935E5b6B4A6778ff292059991',  # UNI DPI-WETH
    #     '0x0954906da0Bf32d5479e25f46056d22f08464cab',  # INDEX
    #     {'from': deployer},
    # )
    ubeswap_oracle = UbeswapV1Oracle.deploy({'from': deployer})
    kp3r_oracle = ERC20KP3ROracle.deploy(ubeswap_oracle, {'from': deployer})
    core_oracle = CoreOracle.deploy({'from': deployer})
    uni_oracle = UniswapV2Oracle.deploy(core_oracle, {'from': deployer})
    proxy_oracle = ProxyOracle.deploy(core_oracle, {'from': deployer})
    core_oracle.setRoute([
        celo_addr,
        cusd_addr,
        ceur_addr,
        ube_addr,
        ube_celo_pool_addr,
    ], [
        kp3r_oracle,
        kp3r_oracle,
        kp3r_oracle,
        kp3r_oracle,
        uni_oracle,
    ], {'from': deployer})
    proxy_oracle.setTokenFactors([
        celo_addr,
        cusd_addr,
        ceur_addr,
        ube_addr,
        ube_celo_pool_addr,
    ], [
        [12500, 8000, 10250],
        [10500, 9500, 10250],
        [10500, 9500, 10250],
        [12500, 8000, 10250],
        [50000, 0, 10250],
    ], {'from': deployer})
    proxy_oracle.setWhitelistERC1155(
        [werc20],
        True,
        {'from': deployer},
    )
    # 
    # TODO: use proxy openzeppeling contract
    # bank_impl = HomoraBank.deploy({'from': deployer})
    # bank_impl.initialize(proxy_oracle, 0, {'from': deployer})
    # bank = TransparentUpgradableProxy(bank_impl, deployer, {'from': deployer})
    bank = HomoraBank.deploy({'from': deployer})
    bank.initialize(proxy_oracle, 0, {'from': deployer})
    # bank.setOracle(proxy_oracle, {'from': deployer})

    uniswap_spell = UniswapV2SpellV1.deploy(
        bank, werc20, ube_router_addr, celo_addr,
        {'from': deployer},
    )

    print('DONE')

    ###########################################################
    # test spells (UNCOMMENT TO TEST)

    # test_uniswap_spell(uniswap_spell, bank, core_oracle)
    # test_uniswap_spell_wstaking(uniswap_spell, bank, wsindex, core_oracle)
    # test_sushiswap_spell(sushiswap_spell, bank, core_oracle)
    # test_sushiswap_spell_wmasterchef(sushiswap_spell, bank, core_oracle)
    # test_balancer_spell(balancer_spell, bank, core_oracle)
    # test_balancer_spell_wstaking(balancer_spell, bank, wsperp, core_oracle)
    # test_curve_spell_wgauge(curve_spell, bank, core_oracle)
