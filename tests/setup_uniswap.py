import pytest


@pytest.fixture(scope='function')
def ufactory(a, MockUniswapV2Factory):
    return MockUniswapV2Factory.deploy(a[0], {'from': a[0]})


@pytest.fixture(scope='function')
def urouter(a, ufactory, MockUniswapV2Router02):
    return MockUniswapV2Router02.deploy(ufactory, {'from': a[0]})
