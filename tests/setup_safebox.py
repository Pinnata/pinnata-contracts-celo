import pytest


@pytest.fixture(scope='function')
def token(a, MockERC20):
    return MockERC20.deploy('token', "TOKEN", 18, {'from': a[0]})


@pytest.fixture(scope='function')
def cToken(a, token, MockCErc20_2):
    return MockCErc20_2.deploy(token, {'from': a[0]})


@pytest.fixture(scope='function')
def safebox(a, cToken, SafeBox):
    return SafeBox.deploy(cToken, "ibToken", "ibTOKEN", {'from': a[0]})
