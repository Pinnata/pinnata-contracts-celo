import pytest


@pytest.fixture(scope='function')
def werc20(a, WERC20):
    return WERC20.deploy({'from': a[0]})

@pytest.fixture(scope='function')
def celo(a, MockERC20):
    return MockERC20.deploy('CELO', 'CELO', 18, {'from': a[0]})

@pytest.fixture(scope='function')
def cusd(a, MockERC20):
    return MockERC20.deploy('cUSD', 'cUSD', 18, {'from': a[0]})

@pytest.fixture(scope='function')
def ceur(a, MockERC20):
    return MockERC20.deploy('cEUR', 'cEUR', 18, {'from': a[0]})

@pytest.fixture(scope='function')
def ube(a, MockERC20):
    return MockERC20.deploy('UBE', 'UBE', 18, {'from': a[0]})


@pytest.fixture(scope='function')
def simple_oracle(a, celo, cusd, ceur, ube, SimpleOracle):
    contract = SimpleOracle.deploy({'from': a[0]})
    contract.setCELOPx(
        [celo, cusd, ceur, ube],
        [2**112, 2**112*10**12//600, 2**112*10**12//600, 2**112//600],
        {'from': a[0]},
    )
    return contract


@pytest.fixture(scope='function')
def core_oracle(a, CoreOracle):
    contract = CoreOracle.deploy({'from': a[0]})
    return contract


@pytest.fixture(scope='function')
def oracle(a, werc20, ProxyOracle, core_oracle):
    contract = ProxyOracle.deploy(core_oracle, {'from': a[0]})
    contract.setWhitelistERC1155([werc20], True, {'from': a[0]})
    return contract


@pytest.fixture(scope='function')
def bank(a, oracle, celo, cusd, ceur, ube, HomoraBank, MockCErc20):
    contract = HomoraBank.deploy({'from': a[0]})
    contract.initialize(oracle, 2000, {'from': a[0]})
    for token in (celo, cusd, ceur, ube):
        cr_token = MockCErc20.deploy(token, {'from': a[0]})
        token.mint(cr_token, '100000 ether', {'from': a[0]})
        contract.addBank(token, cr_token)
    return contract
