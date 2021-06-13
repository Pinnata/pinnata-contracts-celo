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

    dai = interface.IERC20Ex('0x6B175474E89094C44Da98b954EedeAC495271d0F')
    weth = interface.IERC20Ex('0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2')

    mint_tokens(dai, alice)
    mint_tokens(weth, alice)

    dai.approve(homora, 2**256-1, {'from': alice})
    weth.approve(homora, 2**256-1, {'from': alice})

    prevABal = dai.balanceOf(alice)
    prevBBal = weth.balanceOf(alice)
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
            dai,
            weth,
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

    curABal = dai.balanceOf(alice)
    curBBal = weth.balanceOf(alice)

    print('alice delta A Bal', curABal - prevABal)
    print('alice delta B Bal', curBBal - prevBBal)

    prevABal = dai.balanceOf(alice)
    prevBBal = weth.balanceOf(alice)
    prevETHBal = alice.balance()

    position_id = homora.nextPositionId()

    # close the position
    homora.execute(
        position_id - 1,
        uniswap_spell,
        uniswap_spell.removeLiquidityWERC20.encode_input(
            dai,
            weth,
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

    curABal = dai.balanceOf(alice)
    curBBal = weth.balanceOf(alice)
    curETHBal = alice.balance()

    finalABal = curABal
    finalBBal = curBBal
    finalETHBal = curETHBal

    tokenAPrice = oracle.getCELOPx(dai)
    tokenBPrice = oracle.getCELOPx(weth)
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
    weth = interface.IERC20Ex('0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2')
    index = interface.IERC20Ex('0x0954906da0bf32d5479e25f46056d22f08464cab')

    mint_tokens(dpi, alice)
    mint_tokens(weth, alice)

    dpi.approve(homora, 2**256-1, {'from': alice})
    weth.approve(homora, 2**256-1, {'from': alice})

    prevABal = dpi.balanceOf(alice)
    prevBBal = weth.balanceOf(alice)
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
            weth,
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
    curBBal = weth.balanceOf(alice)

    print('alice delta A Bal', curABal - prevABal)
    print('alice delta B Bal', curBBal - prevBBal)

    prevABal = dpi.balanceOf(alice)
    prevBBal = weth.balanceOf(alice)
    prevETHBal = alice.balance()

    position_id = homora.nextPositionId()

    # close the position
    homora.execute(
        position_id - 1,
        uniswap_spell,
        uniswap_spell.removeLiquidityWStakingRewards.encode_input(
            dpi,
            weth,
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
    curBBal = weth.balanceOf(alice)
    curETHBal = alice.balance()

    finalABal = curABal
    finalBBal = curBBal
    finalETHBal = curETHBal

    tokenAPrice = oracle.getCELOPx(dpi)
    tokenBPrice = oracle.getCELOPx(weth)
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


def test_safebox(token, safebox):
    alice = accounts[1]

    mint_tokens(token, alice)

    token.approve(safebox, 2**256-1, {'from': alice})

    deposit_amt = 100 * 10**token.decimals()

    prevBal = token.balanceOf(alice)
    safebox.deposit(deposit_amt, {'from': alice})
    curBal = token.balanceOf(alice)

    assert almostEqual(curBal - prevBal, -deposit_amt), 'incorrect deposit amount'

    withdraw_amt = safebox.balanceOf(alice) // 3

    prevBal = token.balanceOf(alice)
    safebox.withdraw(withdraw_amt, {'from': alice})
    curBal = token.balanceOf(alice)

    assert almostEqual(curBal - prevBal, deposit_amt // 3), 'incorrect first withdraw amount'

    withdraw_amt = safebox.balanceOf(alice)

    prevBal = token.balanceOf(alice)
    safebox.withdraw(withdraw_amt, {'from': alice})
    curBal = token.balanceOf(alice)

    assert almostEqual(curBal - prevBal, deposit_amt - deposit_amt //
                       3), 'incorrect second withdraw amount'


def test_bank(token, bank):
    alice = accounts[1]

    uniswap_spell = UniswapV2SpellV1.at('0xc671B7251a789de0835a2fa33c83c8D4afB39092')

    mint_tokens(token, alice)

    token.approve(bank, 2**256-1, {'from': alice})

    weth = interface.IERC20Ex('0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2')

    amt = 10000 * 10**token.decimals()

    borrow_amt = 10 * 10**token.decimals()

    prevTokenAlice = token.balanceOf(alice)

    bank.execute(0, uniswap_spell, uniswap_spell.addLiquidityWERC20.encode_input(
        token, weth, [amt, 0, 0, borrow_amt, 10**18, 0, 0, 0]), {'from': alice})

    curTokenAlice = token.balanceOf(alice)

    assert almostEqual(curTokenAlice - prevTokenAlice, -amt), 'incorrect input amt'


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
    #TODO: update addresses once fountain deployed
    cycelo_addr = '0x48759F220ED983dB51fA7A8C0D2AAb8f3ce4166a'
    cycusd_addr = '0x76Eb2FE28b36B3ee97F3Adae0C69606eeDB2A37c'
    cyceur_addr = '0xFa3472f7319477c9bFEcdD66E4B948569E7621b9'

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
    # bank.setOracle(proxy_oracle, {'from': deployer})

    uniswap_spell = UniswapV2SpellV1.deploy(
        bank, werc20, ube_router_addr,
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

# deploy safeboxes

    celo = interface.IERC20Ex(celo_addr)
    cusd = interface.IERC20Ex(cusd_addr)
    ceur = interface.IERC20Ex(ceur_addr)
    
    # TODO: uncomment when fountain of youth is deployed

    # cycelo = interface.IERC20Ex(cycelo_addr)
    # cycusd = interface.IERC20Ex(cycusd_addr)
    # cyceur = interface.IERC20Ex(cyceur_addr)

    # safebox_celo = SafeBox.deploy(
    #     cycelo, 'Interest Bearing Celo', 'dCELO', {'from': deployer})
    # safebox_cusd = SafeBox.deploy(
    #     cycusd, 'Interest Bearing Celo US Dollar', 'dcUSD', {'from': deployer})
    # safebox_ceur = SafeBox.deploy(
    #     cyceur, 'Interest Bearing Celo Euro', 'dcEUR', {'from': deployer})

    # # add banks
    # bank.addBank(celo, cycelo_addr, {'from': deployer})
    # bank.addBank(cusd, cycusd_addr, {'from': deployer})
    # bank.addBank(ceur, cyceur_addr, {'from': deployer})


    ###########################################################
    # test cyToken

    # for token in [cyusdt, cyusdc, cyyfi]:
    #     assert interface.IERC20Ex(token).symbol() == 'cy' + \
    #         interface.IERC20Ex(interface.IERC20Ex(token).underlying()).symbol()

    ###########################################################
    # test safeboxes

    # dai = interface.IERC20Ex('0x6B175474E89094C44Da98b954EedeAC495271d0F')
    # usdt = interface.IERC20Ex('0xdAC17F958D2ee523a2206206994597C13D831ec7')
    # usdc = interface.IERC20Ex('0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48')
    # yfi = interface.IERC20Ex('0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e')

    # test_safebox_eth(safebox_eth)
    # test_safebox(dai, safebox_dai)
    # test_safebox(usdt, safebox_usdt)
    # test_safebox(usdc, safebox_usdc)
    # test_safebox(yfi, safebox_yfi)

    ###########################################################
    # test banks with uniswap spell
    # print('============ testing banks =============')

    # test_bank(usdt, bank)
    # test_bank(usdc, bank)