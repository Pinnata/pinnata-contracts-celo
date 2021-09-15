from brownie import (
    accounts,
    HomoraBank,
    SafeBox,
    Contract,
    network,
    interface,
)
import json

network.gas_limit(8000000)

def main():
<<<<<<< HEAD
    deployer = accounts.load('admin')
    f = open('scripts/dahlia_addresses.json')
    addr = json.load(f)['mainnet']

    celo = interface.IERC20Ex(addr['celo'])
    ube = interface.IERC20Ex(addr['ube'])
    btc = interface.IERC20Ex(addr['btc'])
    fcelo = interface.IERC20Ex(addr['fcelo'])
    fube = interface.IERC20Ex(addr['fube'])
    fbtc = interface.IERC20Ex(addr['fbtc'])
    dahlia_bank = HomoraBank.at(addr['dahlia_bank'])

    # # deploy safeboxes

    SafeBox.deploy(
        fcelo, 'Interest Bearing Celo', 'dCELO', {'from': deployer})
    SafeBox.deploy(
        fube, 'Interest Bearing UBE', 'dUBE', {'from': deployer})
    SafeBox.deploy(
        fbtc, 'Interest Bearing BTC', 'dBTC', {'from': deployer})
    
    # add banks
    dahlia_bank.addBank(celo, fcelo, {'from': deployer})
    dahlia_bank.addBank(ube, fube, {'from': deployer})
    dahlia_bank.addBank(btc, fbtc, {'from': deployer})

    dahlia_bank.setWhitelistTokens([celo], [True], {'from': deployer})
    dahlia_bank.setWhitelistTokens([ube], [True], {'from': deployer})
    dahlia_bank.setWhitelistTokens([btc], [True], {'from': deployer})
=======
    deployer = accounts.load('dahlia_admin')

    with open('scripts/dahlia_addresses.json', 'r') as f:
        addr = json.load(f)
    mainnet_addr = addr.get('mainnet')

    celo = interface.IERC20Ex(mainnet_addr.get('celo'))
    mcusd = interface.IERC20Ex(mainnet_addr.get('mcusd'))
    mceur = interface.IERC20Ex(mainnet_addr.get('mceur'))
    ube = interface.IERC20Ex(mainnet_addr.get('ube'))
    scelo = interface.IERC20Ex(mainnet_addr.get('scelo'))
    fcelo = interface.IERC20Ex(mainnet_addr.get('fcelo'))
    fmcusd = interface.IERC20Ex(mainnet_addr.get('fmcusd'))
    fmceur = interface.IERC20Ex(mainnet_addr.get('fmceur'))
    fube = interface.IERC20Ex(mainnet_addr.get('fube'))
    fscelo = interface.IERC20Ex(mainnet_addr.get('fscelo'))
    dahlia_bank = Contract.from_abi("HomoraBank", mainnet_addr.get('dahlia_bank'), HomoraBank.abi)

    # deploy safeboxes
    dcelo = SafeBox.deploy(
        fcelo, 'Interest Bearing Celo', 'dCELO', {'from': deployer})
    dmcusd = SafeBox.deploy(
        fmcusd, 'Interest Bearing mcUSD', 'dmcUSD', {'from': deployer})
    dmceur = SafeBox.deploy(
        fmceur, 'Interest Bearing mcEUR', 'dmcEUR', {'from': deployer})
    dube = SafeBox.deploy(
        fube, 'Interest Bearing UBE', 'dUBE', {'from': deployer})
    dscelo = SafeBox.deploy(
        fscelo, 'Interest Bearing sCELO', 'dsCELO', {'from': deployer})
    
    # add banks
    # dahlia_bank.addBank(celo, fcelo, {'from': deployer})
    # dahlia_bank.addBank(mcusd, fmcusd, {'from': deployer})
    # dahlia_bank.addBank(mceur, fmceur, {'from': deployer})
    # dahlia_bank.addBank(ube, fube, {'from': deployer})
    # dahlia_bank.addBank(scelo, fscelo, {'from': deployer})

    dahlia_bank.setWhitelistTokens([celo, mcusd, mceur, ube, scelo], [True, True, True, True, True], {'from': deployer})

    addr.get('mainnet').update({
        'dcelo': dcelo.address,
        'dmcusd': dmcusd.address,
        'dmceur': dmceur.address, 
        'dube': dube.address,
        'dscelo': dscelo.address,
    })
>>>>>>> kjs/beta_deployment

    print(json.dumps(addr, indent=4), file=open('scripts/dahlia_addresses.json', 'w'))